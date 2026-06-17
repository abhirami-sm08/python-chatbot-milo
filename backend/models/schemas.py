from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
password: str

class LoginResponse(BaseModel):
    access_token: str
token_type: str
full_name: str

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str