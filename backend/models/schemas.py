from pydantic import BaseModel

class LoginRequest(BaseModel):
    unid: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    full_name: str

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str