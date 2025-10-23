from pydantic import BaseModel, EmailStr


class VisitorCreate(BaseModel):
    nickname: str
    email: EmailStr


class Visitor(VisitorCreate):
    id: int

    class Config:
        from_attributes = True


class CodeSubmission(BaseModel):
    nickname: str
    email: EmailStr
    code: str


class JudgeResult(BaseModel):
    status: str
    message: str

