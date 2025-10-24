# backend/Dockerfile

# 1. 使用官方的 Python 3.9 轻量级镜像作为基础
FROM python:3.9-slim

# 2. 在容器内创建一个工作目录 /app
WORKDIR /app

# 3. 将 requirements.txt 文件复制到工作目录中
COPY requirements.txt .

# 添加模块搜索目录
ENV PYTHONPATH=/app

# 4. 安装所有 Python 依赖
# --no-cache-dir 选项可以减小镜像体积
RUN pip install --no-cache-dir -r requirements.txt

# 5. 将你的 app 文件夹复制到工作目录的 app 文件夹中
COPY . .

# 6. 暴露容器的 8000 端口，以便其他容器可以访问它
EXPOSE 8000

# 7. 容器启动时要执行的命令
# 启动 uvicorn 服务器，并监听所有 IP 地址 (0.0.0.0) 的 8000 端口
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]