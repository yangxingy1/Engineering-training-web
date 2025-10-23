# backend/app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas
from typing import Optional


def upsert_visitor_and_update_status(
        db: Session,
        visitor_data: schemas.VisitorCreate,
        ip_address: str,
        user_agent: str,
        judge_status: Optional[str] = None
):
    """
    一个多功能函数，实现以下逻辑:
    1. 根据 nickname 和 email 查找用户。
    2. 如果用户存在，则更新其信息和判题状态。
    3. 如果用户不存在，则创建一个新用户。
    4. 特殊规则：如果用户已有的 judge_status 是 'Accept'，则不再更新它。
    """

    # 步骤 1: 尝试根据昵称和邮箱查找现有用户
    db_visitor = db.query(models.Visitor).filter(
        models.Visitor.nickname == visitor_data.nickname,
        models.Visitor.email == visitor_data.email
    ).first()

    if db_visitor:
        # 步骤 2: 用户已存在，执行更新逻辑
        print(f"用户 {visitor_data.nickname} 已存在，执行更新。")

        # 总是更新IP和User Agent，以记录其最新活动
        db_visitor.ip_address = ip_address
        db_visitor.user_agent = user_agent

        # 仅在需要更新判题状态，且当前状态不是 'Accept' 时才更新
        if judge_status and db_visitor.judge_status != 'Accept':
            db_visitor.judge_status = judge_status

    else:
        # 步骤 3: 用户不存在，创建新用户
        print(f"用户 {visitor_data.nickname} 不存在，创建新记录。")
        db_visitor = models.Visitor(
            nickname=visitor_data.nickname,
            email=visitor_data.email,
            ip_address=ip_address,
            user_agent=user_agent,
            judge_status=judge_status
        )
        db.add(db_visitor)

    # 步骤 4: 提交更改到数据库并返回用户实例
    db.commit()
    db.refresh(db_visitor)
    return db_visitor

