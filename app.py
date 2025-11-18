import gradio as gr
import subprocess
import os
import shutil
from pathlib import Path
import time
import sys

# ================= 配置区域 (请根据实际情况修改) =================

# 基础路径 setup
BASE_DIR = Path(__file__).parent.absolute()
PROJECT1_DIR = BASE_DIR / "voice_filter"
PROJECT2_DIR = BASE_DIR / "voice_clone_video_synthesis"

# voice_clone_video_synthesis 需要的配置路径
CHECKPOINT_CONFIG = "./checkpoints/config.yaml"
CHECKPOINT_MODEL_DIR = "./checkpoints"

# 输出目录
OUTPUT_DIR = BASE_DIR / "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ================= 核心处理逻辑 =================

def run_pipeline(video_file, subtitle_file, progress=gr.Progress()):
    """
    全自动流程：1. 分离音轨 (voice_filter) -> 2. AI配音合成 (voice_clone_video_synthesis) -> 3. FFmpeg 合并
    这是一个生成器函数，用于实时流式输出日志到 Gradio 界面。
    """
    # 初始化日志记录
    log_history = "--- 启动日志 ---"
    
    def log(message):
        """记录日志，并 yield 到 Gradio Textbox"""
        nonlocal log_history
        # 记录到终端（stderr确保可见性）
        print(message, file=sys.stderr) 
        # 记录到 Gradio UI
        log_history += message + "\n"
        # yield 返回当前日志状态，以及视频/音频的空/旧值
        return log_history, gr.update(value=None), gr.update(value=None) 

    yield log("检查输入文件...")
    if not video_file or not subtitle_file:
        yield log("错误：请确保上传了视频文件和字幕文件！"), None, None
        return

    timestamp = int(time.time())
    
    # 路径准备
    input_video_path = Path(video_file)
    input_subtitle_path = Path(subtitle_file)
    
    # 定义中间和最终输出路径
    p1_video_clean = OUTPUT_DIR / f"clean_video_{timestamp}.mp4"
    p1_vocal = OUTPUT_DIR / f"vocal_{timestamp}.wav"
    p1_background = OUTPUT_DIR / f"background_{timestamp}.wav"
    p2_final_audio = OUTPUT_DIR / f"final_audio_cn_{timestamp}.wav"
    p2_tmp_dir = OUTPUT_DIR / f"tmp_p2_{timestamp}"
    os.makedirs(p2_tmp_dir, exist_ok=True)
    final_video_output = OUTPUT_DIR / f"final_result_{timestamp}.mp4"

    # =======================================================
    # 阶段 1: 运行 voice_filter (分离音轨 & 提取纯画面)
    # =======================================================
    progress(0.1, desc="[1/3] 正在准备 voice_filter 环境...")
    yield log("\n--- 阶段 1/3: 启动音轨分离 (voice_filter) ---")
    
    # 修复：创建 voice_filter 模型目录 (解决 FileNotFoundError)
    P1_MODEL_DIR = PROJECT1_DIR / "data" / "audio-separator-models"
    try:
        os.makedirs(P1_MODEL_DIR, exist_ok=True)
        yield log(f"确保 voice_filter 模型目录存在: {P1_MODEL_DIR}")
    except Exception as e:
        yield log(f"错误: 无法创建 voice_filter 模型目录。{e}"), None, None
        return

    cmd1 = (
        f"source envs.sh && "
        f"uv run main.py "
        f"--video_path '{input_video_path}' "
        f"--video_output '{p1_video_clean}' "
        f"--audio_mixed '{OUTPUT_DIR / f'mixed_orig_{timestamp}.wav'}' "
        f"--vocal '{p1_vocal}' "
        f"--background '{p1_background}'"
    )
    
    yield log(f"=== 运行命令 (voice_filter): {cmd1}")
    
    try:
        p1 = subprocess.Popen(
            ["bash", "-c", cmd1], 
            cwd=PROJECT1_DIR, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True, 
            bufsize=1
        )
        
        # 实时读取并更新日志和进度
        progress(0.15, desc="[1/3] 正在运行 voice_filter...")
        for line in p1.stdout:
            yield log(line.strip()) 
            # 粗略更新进度，防止界面卡顿
            current_progress = 0.15 + (0.2 * len(log_history) / 5000) 
            progress(min(current_progress, 0.38), desc="[1/3] 正在运行 voice_filter...")

        p1.wait()
        
        if p1.returncode != 0:
            raise subprocess.CalledProcessError(p1.returncode, cmd1)

    except subprocess.CalledProcessError as e:
        yield log(f"voice_filter 运行失败，退出码: {e.returncode}. 确保模型已下载且未损坏。"), None, None
        return
    
    progress(0.4, desc="[1/3] 音轨分离完成。")
    yield log("--- 阶段 1/3 完成：音轨分离成功。---")

    if not p1_video_clean.exists():
        yield log("错误: voice_filter 未生成纯画面视频文件，流程中断。"), None, None
        return

    # =======================================================
    # 阶段 2: 运行 voice_clone_video_synthesis (AI配音与合成)
    # =======================================================
    progress(0.45, desc="[2/3] 正在准备 voice_clone_video_synthesis 环境...")
    yield log("\n--- 阶段 2/3: 启动 AI 配音合成 (voice_clone_video_synthesis) ---")

    cmd2 = (
        # f"source envs.sh && " 
        f"uv run main.py "
        f"-v '{p1_vocal}' "
        f"-s '{input_subtitle_path}' "
        f"-b '{p1_background}' "
        f"-o '{p2_final_audio}' "
        f"-t '{p2_tmp_dir}' "
        f"-c '{CHECKPOINT_CONFIG}' "
        f"-m '{CHECKPOINT_MODEL_DIR}'"
    )

    yield log(f"=== 运行命令 (voice_clone_video_synthesis): {cmd2}")

    try:
        p2 = subprocess.Popen(
            ["bash", "-c", cmd2], 
            cwd=PROJECT2_DIR, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True, 
            bufsize=1
        )
        
        # 实时读取并更新日志
        progress(0.5, desc="[2/3] 正在运行 voice_clone_video_synthesis...")
        for line in p2.stdout:
            yield log(line.strip())
            current_progress = 0.5 + (0.3 * len(log_history) / 10000)
            progress(min(current_progress, 0.78), desc="[2/3] 正在运行 voice_clone_video_synthesis...")
        
        p2.wait()

        if p2.returncode != 0:
            raise subprocess.CalledProcessError(p2.returncode, cmd2)

    except subprocess.CalledProcessError as e:
        yield log(f"voice_clone_video_synthesis 运行失败，退出码: {e.returncode}. 请检查详细日志。"), None, None
        return

    progress(0.8, desc="[2/3] 配音合成完成。")
    yield log("--- 阶段 2/3 完成：配音合成成功。---")

    if not p2_final_audio.exists():
        yield log("错误: voice_clone_video_synthesis 未生成最终音频文件，流程中断。"), None, None
        return

    # =======================================================
    # 阶段 3: 使用 FFmpeg 合并 画面 + 新音频
    # =======================================================
    progress(0.85, desc="[3/3] 正在合并最终视频 (FFmpeg)...")
    yield log("\n--- 阶段 3/3: 启动 FFmpeg 合并 ---")
    
    cmd_merge = [
        "ffmpeg", "-y",
        "-i", str(p1_video_clean),
        "-i", str(p2_final_audio),
        "-c:v", "copy",
        "-c:a", "aac",
        "-strict", "experimental",
        str(final_video_output)
    ]
    
    yield log(f"=== 运行命令 (FFmpeg): {' '.join(cmd_merge)}")
    
    try:
        # FFmpeg 使用 run 阻塞执行
        subprocess.run(cmd_merge, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        yield log(f"视频合并失败。请确认系统中已安装 ffmpeg。错误详情: {e.stderr}"), None, None
        return

    # 清理临时目录 (可选)
    shutil.rmtree(p2_tmp_dir, ignore_errors=True)
    
    progress(1.0, desc="全部完成！")
    final_message = "✅ 全部流程成功完成！"
    # 最终 yield 返回所有结果
    yield log(final_message), str(final_video_output), str(p2_final_audio)

# ================= 构建 UI 界面 =================

# 定义 Gradio 界面，注意添加 log_output
with gr.Blocks(title="自动视频配音系统", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # 🎬 MORTIS--视频中文AI翻配系统
        上传 **原始视频** 和 **JSON字幕**，系统将自动执行：音轨分离、AI配音、视频合成。
        **重要提示:** 流程可能需要几分钟。请关注下方的 **实时日志** 获取进度反馈。
        """
    )
    
    with gr.Row():
        with gr.Column(scale=1):
            video_input = gr.Video(label="1. 上传原视频 (MKV/MP4)", sources=["upload"])
            json_input = gr.File(label="2. 上传字幕文件 (JSON)", file_types=[".json"])
            submit_btn = gr.Button("🚀 开始全自动处理", variant="primary", size="lg")
        
        with gr.Column(scale=1):
            output_video = gr.Video(label="📺 处理结果：最终汉化视频", interactive=False)
            output_audio = gr.Audio(label="🎵 仅播放音频 (检查用)", type="filepath")
            
    # 新增日志输出框
    # 将日志输出框作为 run_pipeline 的第一个输出
    log_output = gr.Textbox(label="实时日志输出", lines=15, autoscroll=True, interactive=False, value="等待上传文件并点击 '开始全自动处理'...")

    # 更新 click 事件，以处理 generator function 和新的输出
    submit_btn.click(
        fn=run_pipeline,
        inputs=[video_input, json_input],
        outputs=[log_output, output_video, output_audio]
    )

if __name__ == "__main__":
    print(f"Server starting... Outputs will be saved to: {OUTPUT_DIR}")
    demo.queue().launch(
        server_name="0.0.0.0", 
        root_path=None, 
        allowed_paths=[BASE_DIR, "/hy-tmp", "/private/var/folders"]
    )