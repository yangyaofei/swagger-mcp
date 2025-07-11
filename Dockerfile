FROM python:3.12-slim
WORKDIR /app

COPY ./ /app/
RUN pip install --no-cache-dir -r requirements.txt
# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["fastmcp", "run", "server_start.py", "--transport", "streamable-http", "--host", "0.0.0.0"]