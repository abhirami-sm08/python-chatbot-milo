from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    full_name: str


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


class ComplaintRequest(BaseModel):
    subject: str
    description: str
    loan_id: int | None = None


class ComplaintResponse(BaseModel):
    complaint_id: int
    status: str
    message: str
