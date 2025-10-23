# backend/judge/run_sandbox.py
import docker
import os
import tempfile
import json
from pathlib import Path

# 定义固定的题目和测试用例
# 题目：读取两行，每行一个整数，输出它们的和
TEST_CASES = [
    {"input": "2\n3\n", "output": "5\n"},
    {"input": "-10\n10\n", "output": "0\n"},
    {"input": "100\n200\n", "output": "300\n"},
    {"input": "0\n100\n", "output": "100\n"},
    {"input": "100\n0\n", "output": "100\n"}
]

# 定义沙箱 Docker 镜像的名称和 Dockerfile 路径
IMAGE_NAME = "python-sandbox-env"
DOCKERFILE_PATH = str(Path(__file__).parent.resolve()) # 获取 Dockerfile.sandbox 所在目录

# 初始化 Docker 客户端
try:
    client = docker.from_env()
except docker.errors.DockerException:
    raise RuntimeError("Docker运行错误: 请检查Docker服务安装/启动")

def build_sandbox_image():
    """构建或检查沙箱 Docker 镜像是否存在"""
    try:
        client.images.get(IMAGE_NAME)
        print(f"沙盒镜像: '{IMAGE_NAME}' 已存在.")
    except docker.errors.ImageNotFound:
        print(f"没有找到沙盒镜像: '{IMAGE_NAME}'. 镜像搭建中...")
        client.images.build(
            path=DOCKERFILE_PATH,
            dockerfile="Dockerfile.sandbox",
            tag=IMAGE_NAME,
            rm=True     # 构建成功后删除中间层
        )
        print("成功搭建沙盒镜像.")

# 首次加载模块时构建镜像
build_sandbox_image()

def judge_code(user_code: str) -> dict:
    """
    在 Docker 沙箱中运行用户代码并进行评判
    """
    # 使用 tempfile 模块创建一个安全的临时目录
    # 这可以避免多用户同时提交时发生文件冲突
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # 1. 将用户代码写入 submission.py
        (temp_path / "submission.py").write_text(user_code, encoding='utf-8')

        # 2. 遍历所有测试用例
        for i, case in enumerate(TEST_CASES):
            (temp_path / "input.txt").write_text(case["input"], encoding='utf-8')

            try:
                # 3. 运行 Docker 容器
                container = client.containers.run(
                    image=IMAGE_NAME,
                    # 将临时目录挂载到容器的 /sandbox 目录
                    # read-only (ro) 确保容器不能修改挂载的目录
                    volumes={str(temp_path): {'bind': '/sandbox', 'mode': 'ro'}},
                    # 覆盖默认的 CMD，重定向标准输入
                    command="sh -c 'python submission.py < input.txt'",
                    # --- 安全与资源限制 ---
                    user=1000,  # 使用低权限用户运行
                    network_disabled=True,  # 禁用所有网络访问
                    mem_limit="64m",    # 内存限制: 64MB
                    remove=True,    # 运行结束后自动删除容器
                    detach=False,   # 在前台运行，等待其完成
                )

                # 4. 获取程序的输出并解码
                actual_output = container.decode('utf-8')

                # 5. 比对输出结果
                # .strip() 用于去除末尾可能多余的换行或空格
                if actual_output.strip() != case["output"].strip():
                    return {"status": "Wrong Answer", "message": f"测试用例 {i+1} 未通过。"}

            except docker.errors.ContainerError as e:
                # 容器运行出错 (例如，代码有运行时错误)
                error_message = e.stderr.decode('utf-8') if e.stderr else "未知运行错误"
                return {"status": "Runtime Error", "message": error_message}
            except Exception as e:
                # 其他 Docker 错误
                return {"status": "System Error", "message": f"判题系统出现错误: {str(e)}"}

    # 6. 如果所有用例都通过
    return {"status": "Accept", "message": "所有测试用例均已通过！"}
