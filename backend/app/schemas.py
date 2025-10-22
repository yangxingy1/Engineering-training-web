from pydantic import BaseModel, EmailStr


class VisitorCreate(BaseModel):
    nickname: str
    email: EmailStr


class Visitor(VisitorCreate):
    id: int

    class Config:
        from_attributes = True
