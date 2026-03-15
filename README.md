# 🎬 MORTIS视频中文AI翻配系统
![tmp_file609d1431c1afafb03e58bfa7bab33e98328979125](https://github.com/user-attachments/assets/e890dd15-c0f9-4710-8931-3253a08befe6)

**Multimodal Oral Real-time TTS Intelligent Synthesis**

本项目提供了一个端到端的解决方案，用于将含有外语对白和背景音乐的视频，自动处理为含有中文配音的视频。整个流程通过一个用户友好的 Gradio 界面启动，并在后台自动执行音轨分离、AI 语音合成和最终视频合并。

## 📺 效果展示

输入视频：
<video src="./input.mp4" controls width="600"></video>

输出视频：
<video src="./output.mp4" controls width="600"></video>

## ✨ 项目特点

- **全流程自动化**：一键完成从视频上传到最终配音视频输出的所有步骤。
- **实时日志**：通过 Gradio 界面实时显示 `voice_filter` 和 `voice_clone_video_synthesis` 的执行输出，方便追踪进度和诊断问题。
- **音轨分离**：利用 `voice_filter` 模块，有效分离原始人声和背景音乐。
- **高保真配音**：利用 `voice_clone_video_synthesis` 模块，根据 JSON 字幕和背景音，生成高质量的中文目标音频。

## ⚙️ 架构概览

本项目由一个主应用程序 (`app.py`) 和两个独立的子模块（`voice_filter` 和 `voice_clone_video_synthesis`）构成：

- **app.py (Gradio 界面)**：负责用户交互、文件上传，并协调执行以下两个子进程。
- **voice_filter（音轨分离）**：负责从上传的视频中提取纯净的背景音轨，并输出无声的纯画面视频。
- **voice_clone_video_synthesis（AI 配音）**：负责根据提供的字幕文件，使用 TTS 模型生成目标语言人声，并与背景音轨混合，创建最终音频。

## 🚀 环境设置与运行指南

### 1. 目录结构（确认）

请确保您的项目目录结构如下：

```
./MORTIS/
├── voice_filter/                            # 音轨分离模块
│   ├── envs.sh
│   ├── main.py
│   └── ...
├── voice_clone_video_synthesis/             # AI 配音模块
│   ├── checkpoints/                         # **模型权重文件存放目录**
│   │   ├── config.yaml
│   │   ├── <大型模型权重文件> (e.g., .pth, .pt)
│   │   └── 其他文件
│   ├── envs.sh
│   ├── main.py
│   └── ...
├── output/                                  # 结果输出目录
└── app.py                                   # Gradio 主程序
```

### 2. 依赖安装

依赖的Python版本：Python >= 3.10

请确保两个子项目都已安装了各自的依赖环境 (`.venv`)。推荐使用 `uv` 工具进行快速环境管理：

```bash
# 安装gradio
pip install gradio

# 激活 voice_filter 环境
cd ./MORTIS/voice_filter/
uv venv
# 确保所有依赖已同步 (根据您实际的依赖管理方式执行)
uv sync

# 激活 voice_clone_video_synthesis 环境
cd ./MORTIS/voice_clone_video_synthesis/
uv venv
# 确保所有依赖已同步
uv sync
```

### 3. 模型文件准备（关键）

AI 模型的权重文件会自动下载，但如果程序出现程序将静默卡死或报错，则需要手动下载并放置到指定位置：

- **voice_filter 模型**：首次运行时会自动尝试创建./MORTIS/voice_filter/data/audio-separator-models目录并在其中下载 `download_checks.json` `model_bs_roformer_ep_317_sdr_12.9755.ckpt` `model_bs_roformer_ep_317_sdr_12.9755.ckpt` 到 `model_bs_roformer_ep_317_sdr_12.9755.yaml`。如果有网速问题或者下载失败，请自行搜索相关文件并手动下载后放置此处。

- **voice_clone_video_synthesis 模型**：

该模型不会自动下载，你需要提前在voice_clone_video_synthesis目录下运行：

```bash
uv tool install "huggingface-hub[cli,hf_xet]"

hf download IndexTeam/IndexTTS-2 --local-dir=checkpoints
```
运行完成会自动尝试在voice_clone_video_synthesis目录下创建一个checkpoints文件夹，其中包含`config.yaml` 和将大型模型权重文件（通常是 `.pth` 或 `.pt` 文件）。如果有网速问题或者下载失败，请自行搜索IndexTeam/IndexTTS-2项目文件并手动下载后放置此处。

- **.hf_cache 问题**：

如果你运行到：
```bash
- loading tts2...
GPT2InferenceModel has generative capabilities, as `prepare_inputs_for_generation` is explicitly overwritten. However, it doesn't directly inherit from `GenerationMixin`. From 👉v4.50👈 onwards, `PreTrainedModel` will NOT inherit from `GenerationMixin`, and this model will lose the ability to call `generate` and other related functions.
- If you're using `trust_remote_code=True`, you can get rid of this warning by loading the model with an auto class. See https://huggingface.co/docs/transformers/en/model_doc/auto#auto-classes
- If you are the owner of the model architecture code, please modify your model class such that it inherits from `GenerationMixin` (after `PreTrainedModel`, otherwise you'll get an exception).
- If you are not the owner of the model architecture class, please contact the model code owner to update it.
```
这一步后终端无响应，你可以观察到在voice_clone_video_synthesis目录下创建了.hf_cache文件夹，其中正在下载其他依赖的模型文件。无响应的原因同样是下载速度过慢导致。请尝试更换网络或者在voice_clone_video_synthesis目录下先单独运行voice_clone_video_synthesis项目尝试下载或者自行下载：
```bash
uv run main.py -v ./data/测试纯人声.wav -s ./data/测试字幕.json -b ./data/测试背景音.wav -o ./data/输出混音.wav -t ./tmp -c ./checkpoints/config.yaml -m ./checkpoints
```

### 4. 启动应用

返回到项目根目录，并启动 Gradio 应用：

```bash
cd ./MORTIS/
python app.py
```

## 📝 使用方法

1. **访问链接**：浏览器打开终端中显示的本地或公共 Gradio 链接（http://0.0.0.0:7860/）。

2. **上传文件**：
   - 将 **原始视频文件** 上传到第一个输入框。
   - 将 **JSON 字幕文件**（包含时间戳和文本）上传到第二个输入框。获取字幕文件可以使用工具 https://gitee.com/lyx0212/subtitle_agent 进行提取，JSON字幕文件的格式参考如下，如果你已有ass或srt格式的字幕文件，可以使用LLM将其转换成下面的格式：
```bash
[
  {
    "start_time": "00:00:00,000",
    "end_time": "00:00:06,720",
    "speaker_id": "spk_0",
    "dialogue_content": "你都说到这个份上了，那就没办法了。我看我暂时放弃交男友好了。",
    "emotion_label": "平静",
    "emotion_intensity": 2
  },
  {
    "start_time": "00:00:06,720",
    "end_time": "00:00:10,720",
    "speaker_id": "spk_0",
    "dialogue_content": "不，你不用顾虑我。",
    "emotion_label": "惊讶",
    "emotion_intensity": 2
  },
  {
    "start_time": "00:00:10,720",
    "end_time": "00:00:11,300",
    "speaker_id": "spk_0",
    "dialogue_content": "怎么了吗？",
    "emotion_label": "平静",
    "emotion_intensity": 2
  },
    {
    "start_time": "00:00:11,300",
    "end_time": "00:00:14,360",
    "speaker_id": "spk_0",
    "dialogue_content": "我们刚才有碰到姬宫同学他们对吧？",
    "emotion_label": "平静",
    "emotion_intensity": 2
  },
  {
    "start_time": "00:00:14,360",
    "end_time": "00:00:21,960",
    "speaker_id": "spk_0",
    "dialogue_content": "代表他们已经知道你是跟文艺社的人来玩不是吗，要是你上传了约会的照片...",
    "emotion_label": "平静",
    "emotion_intensity": 2
  }
]
```
3. **开始处理**：点击 **"🚀 开始全自动处理"** 按钮。

4. **实时监控**：关注下方的 **"实时日志输出"** 文本框。程序将流式显示 `voice_filter` 和 `voice_clone_video_synthesis` 的每一步执行信息（包括模型加载和计算进度）。

5. **查看结果**：流程完成后，最终的配音视频将在 **"处理结果：最终汉化视频"** 区域显示。

---
