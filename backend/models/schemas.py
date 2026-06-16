from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr # type: ignore
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str    # <--- Indented with 4 spaces / 1 tab
    full_name: str     # <--- Indented with 4 spaces / 1 tab

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str