# 使用多阶段构建，支持多平台
FROM python:3.12-slim as builder

# 构建参数
ARG TARGETPLATFORM
ARG BUILDPLATFORM
ARG BUILDTIME
ARG VERSION
ARG REVISION

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装构建依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt pyproject.toml ./

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 生产阶段
FROM python:3.12-slim

# 构建参数和标签
ARG TARGETPLATFORM
ARG BUILDPLATFORM
ARG BUILDTIME
ARG VERSION
ARG REVISION

LABEL org.opencontainers.image.title="swagger-mcp" \
      org.opencontainers.image.description="OpenAPI/Swagger 文档分析工具" \
      org.opencontainers.image.vendor="Vibe Coding" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.created="${BUILDTIME}" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${REVISION}" \
      org.opencontainers.image.source="https://github.com/username/swagger-mcp"

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.local/bin:$PATH"

# 创建非 root 用户
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# 设置工作目录
WORKDIR /app

# 从构建阶段复制依赖
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制项目文件
COPY --chown=appuser:appuser swagger_mcp/ ./swagger_mcp/
COPY --chown=appuser:appuser requirements.txt pyproject.toml ./

# 切换到非 root 用户
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from swagger_mcp.server import mcp; print('Server OK')" || exit 1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["fastmcp", "run", "swagger_mcp/server.py"] 