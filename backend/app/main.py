# 配置日志
# 创建数据库表
# CORS中间件
# API端点
import os
from fastapi import FastAPI, Depends, Request
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from . import crud, models, schemas
from .database import engine, get_db

# --- 1. Loguru 配置 ---
# 确保日志文件目录存在
if not os.path.exists('logs'):
    os.makedirs('logs')

# 移除默认处理器并添加我们自己的配置
logger.remove()
log_format = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
    "IP: {extra[ip]: <15} | User-Agent: {extra[user_agent]} | "
    "Message: {message}"
)
logger.add(
    sink="logs/visitors.log",
    format=log_format,
    level="INFO",
    rotation="10 MB",       # 当文件达到 10MB 时轮转
    compression="zip",      # 压缩旧的日志文件
    enqueue=True,           # 异步写入，不阻塞主线程
    backtrace=True,         # 在异常时记录完整的堆栈跟踪
    diagnose=True
)

# --- 2. 数据库表创建 ---
# 这行代码会根据 models.py 中的定义，在数据库中创建表（如果表不存在）
models.Base.metadata.create_all(bind=engine)

# --- 3. FastAPI 应用实例 ---
app = FastAPI()

# --- 4. CORS 跨域配置 ---
# 允许所有来源访问 API，方便开发。在生产环境中可以收紧。
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 5. API 端点 ---
@app.post("/api/submit", response_model=schemas.Visitor)
def submit_form(visitor: schemas.VisitorCreate, request: Request, db: Session = Depends(get_db)):
    """
    接收访客提交的昵称和邮箱，存入数据库并记录日志。
    """
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "unknown")

    # 步骤 A: 将数据存入数据库
    db_visitor = crud.create_visitor(db=db, visitor=visitor, ip_address=client_ip, user_agent=user_agent)

    # 步骤 B: 使用 Loguru 记录日志
    # 使用 .bind() 来为本次日志记录绑定上下文信息
    context_logger = logger.bind(ip=client_ip, user_agent=user_agent)
    context_logger.info(f"New submission received: Nickname='{visitor.nickname}', Email='{visitor.email}'")

    return db_visitor

@app.get("/")
def read_root():
    """
    一个简单的根端点，用于检查 API 是否正常运行。
    """
    logger.bind(ip="N/A", user_agent="HealthCheck").info("Root endpoint was accessed.")
    return {"message": "Welcome to the Innovation Base API"}