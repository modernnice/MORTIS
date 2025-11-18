FROM python:3.10

WORKDIR /app

# 1. 安装系统依赖
RUN apt update && apt install -y ffmpeg

# 2. 设置 pip 源、安装uv
RUN pip install --upgrade pip \
    && pip config set global.index-url https://mirrors.aliyun.com/pypi/simple \
    && pip install uv

# 3. 复制锁文件
COPY uv.lock pyproject.toml /app/
ENV UV_HTTP_TIMEOUT=600

# 4. 安装依赖
RUN uv sync

COPY . /app

COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh


ENTRYPOINT ["/app/start.sh"]
