from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import login,chat


app = FastAPI(
title="Milo RAG Banking Backend"
)

app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

app.include_router(
login.router,
prefix="/api"
)

app.include_router(
chat.router,
prefix="/api"
)

@app.get("/")
def health_check():
    return {
    "status": "Milo Engine Running"
}
