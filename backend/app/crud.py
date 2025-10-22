from sqlalchemy.orm import Session
from . import models, schemas

def create_visitor(db: Session, visitor:schemas.VisitorCreate, ip_address: str, user_agent: str):
    db_visitor = models.Visitor(
        nickname=visitor.nickname,
        email=visitor.email,
        ip_address=ip_address,
        user_agent=user_agent
    )
    # 添加到会话
    db.add(db_visitor)
    # 提交
    db.commit()
    # 刷新更新
    db.refresh(db_visitor)
    return db_visitor
