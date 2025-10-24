# backend/judge/run_sandbox.py
import docker
import os
import uuid
from pathlib import Path

# --- 共享卷配置 ---
# 这是共享卷挂载到 backend 容器内部的路径。
CONTAINER_SHARED_PATH = Path("/app/judge_tmp")
# 这是项目在宿主机上的绝对路径。我们需要它来告诉 Docker 守护进程在哪里找到要挂载到沙箱的文件。
# 我们通过环境变量来获取以增加灵活性，但提供一个默认值。
# !!重要!!: 如果你的项目不在 /root/gc_training，请修改这里的默认值
HOST_PROJECT_PATH = Path(os.environ.get("HOST_PROJECT_PATH", f"/root/zyz/project_python/gc_training"))
HOST_SHARED_PATH = HOST_PROJECT_PATH / "backend" / "judge_tmp"

# 确保共享目录存在
CONTAINER_SHARED_PATH.mkdir(exist_ok=True)

# ... (TEST_CASES, IMAGE_NAME 等保持不变) ...
TEST_CASES = [
    {"input": "2\n3\n", "output": "5\n"},
    {"input": "-10\n10\n", "output": "0\n"},
    {"input": "0\n200\n", "output": "200\n"},
    {"input": "200\n0\n", "output": "200\n"},
    {"input": "0\n-200\n", "output": "-200\n"},
    {"input": "-200\n0\n", "output": "-200\n"},
    {"input": "100\n200\n", "output": "300\n"},
    {"input": "-100\n-200\n", "output": "-300\n"}
]
IMAGE_NAME = "python-sandbox-env"
DOCKERFILE_PATH = str(Path(__file__).parent.resolve())

# 初始化 Docker 客户端
try:
    api_client = docker.APIClient(timeout=60)
    client = docker.DockerClient(api_client=api_client)
    client.ping()
except Exception:
    raise RuntimeError("Docker is not running, not installed, or the Docker daemon is unresponsive.")


def build_sandbox_image():
    try:
        client.images.get(IMAGE_NAME)
    except docker.errors.ImageNotFound:
        print(f"Sandbox image '{IMAGE_NAME}' not found. Building...")
        client.images.build(path=DOCKERFILE_PATH, dockerfile="Dockerfile.sandbox", tag=IMAGE_NAME, rm=True)
        print("Sandbox image built successfully.")


build_sandbox_image()


def judge_code(user_code: str) -> dict:
    # 为本次提交创建一个唯一的目录，以避免冲突。
    submission_id = str(uuid.uuid4())

    # backend 容器内部的路径
    container_submission_path = CONTAINER_SHARED_PATH / submission_id
    container_submission_path.mkdir()

    # 宿主机上的路径
    host_submission_path = HOST_SHARED_PATH / submission_id

    try:
        # 1. 将用户代码和输入文件写入共享目录。
        (container_submission_path / "submission.py").write_text(user_code, encoding='utf-8')

        for i, case in enumerate(TEST_CASES):
            (container_submission_path / "input.txt").write_text(case["input"], encoding='utf-8')

            try:
                # 2. 运行 Docker 容器，并挂载宿主机路径。
                container_output = client.containers.run(
                    image=IMAGE_NAME,
                    # 这是关键的改动：使用宿主机路径作为卷的来源。
                    volumes={str(host_submission_path): {'bind': '/sandbox', 'mode': 'rw'}},
                    command="sh -c 'python submission.py < input.txt'",
                    user=1000,
                    network_disabled=True,
                    mem_limit="64m",
                    remove=True,
                    detach=False,
                )

                actual_output = container_output.decode('utf-8')

                if actual_output.strip() != case["output"].strip():
                    return {"status": "Wrong Answer", "message": f"测试用例 {i + 1} 未通过。"}

            except docker.errors.ContainerError as e:
                error_message = e.stderr.decode('utf-8') if e.stderr else "未知运行错误"
                return {"status": "Runtime Error", "message": error_message}
            except Exception as e:
                return {"status": "System Error", "message": f"判题系统出现错误: {str(e)}"}

    finally:
        # 3. 清理共享卷中的本次提交目录。
        import shutil
        shutil.rmtree(container_submission_path, ignore_errors=True)

    return {"status": "Accept", "message": "所有测试用例均已通过！"}