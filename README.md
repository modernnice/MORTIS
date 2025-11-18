🎬 MORTIS视频中文AI翻配系统 (Multimodal Oral Real-time TTS Intelligent Synthesis)

本项目提供了一个端到端的解决方案，用于将含有外语对白和背景音乐的视频，自动处理为含有中文配音的视频。整个流程通过一个用户友好的 Gradio 界面启动，并在后台自动执行音轨分离、AI 语音合成和最终视频合并。

✨ 项目特点

全流程自动化： 一键完成从视频上传到最终配音视频输出的所有步骤。

实时日志： 通过 Gradio 界面实时显示voice_filter和voice_clone_video_synthesis的执行输出，方便追踪进度和诊断问题。

音轨分离： 利用voice_filter模块，有效分离原始人声和背景音乐。

高保真配音： 利用voice_clone_video_synthesis模块，根据 JSON 字幕和背景音，生成高质量的中文目标音频。

⚙️ 架构概览

本项目由一个主应用程序 (app.py) 和两个独立的子模块（voice_filter和 voice_clone_video_synthesis）构成：

app.py (Gradio 界面): 负责用户交互、文件上传，并协调执行以下两个子进程。

voice_filter(音轨分离): 负责从上传的视频中提取纯净的背景音轨，并输出无声的纯画面视频。

voice_clone_video_synthesis (AI 配音): 负责根据提供的字幕文件，使用 TTS 模型生成目标语言人声，并与背景音轨混合，创建最终音频。

🚀 环境设置与运行指南

1. 目录结构（确认）

请确保您的项目目录结构如下：

./MORTIS/
├── voice_filter/                            # 音轨分离模块
│   ├── envs.sh
│   ├── main.py
│   └── ...
├── voice_clone_video_synthesis/         # AI 配音模块
│   ├── checkpoints/                     # **模型权重文件存放目录**
│   │   ├── config.yaml
│   │   └── <大型模型权重文件> (e.g., .pth, .ckpt)
│   ├── envs.sh
│   └── main.py
├── output/                              # 结果输出目录
├── app.py                               # Gradio 主程序


2. 依赖安装

请确保两个子项目都已安装了各自的依赖环境 (.venv)。推荐使用 uv 工具进行快速环境管理：

# 激活voice_filter环境
cd ./MORTIS/voice_filter/
uv venv
# 确保所有依赖已同步 (根据您实际的依赖管理方式执行)
uv sync 

# 激活voice_clone_video_synthesis环境
cd ./MORTIS/voice_clone_video_synthesis/
uv venv
# 确保所有依赖已同步 
uv sync


3. 模型文件准备（关键）

AI 模型的权重文件需要手动下载并放置到指定位置，否则程序将静默卡死或报错：

voice_filter模型： 首次运行时会自动尝试下载 model_bs_roformer_ep_317_sdr_12.9755.ckpt 到 voice_filter/data/audio-separator-models/。如果下载失败，请手动下载后放置此处。

voice_clone_video_synthesis模型：

将 config.yaml 放置在：voice_clone_video_synthesis/checkpoints/

将大型模型权重文件（通常是 .pth 或 .ckpt 文件）放置在：voice_clone_video_synthesis/checkpoints/

4. 启动应用

返回到项目根目录，并启动 Gradio 应用：

cd ./MORTIS/
python app.py


📝 使用方法

访问链接： 浏览器打开终端中显示的本地或公共 Gradio 链接。

上传文件：

将 原始视频文件 上传到第一个输入框。

将 JSON 字幕文件（包含时间戳和文本）上传到第二个输入框。

开始处理： 点击 "🚀 开始全自动处理" 按钮。

实时监控： 关注下方的 “实时日志输出” 文本框。程序将流式显示voice_filter和voice_clone_video_synthesis的每一步执行信息（包括模型加载和计算进度）。

查看结果： 流程完成后，最终的配音视频将在 “处理结果：最终汉化视频” 区域显示。