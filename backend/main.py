import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.routes import login, chat
from backend.admin.dashboard import router as admin_router
from backend.admin.analytics import router as analytics_router

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

# --- API Routers ---
app.include_router(login.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")

# --- Project root (one level up from backend/) ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
IMAGES_DIR = os.path.join(PROJECT_ROOT, "images")

# --- Static file mounts ---
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")


# --- HTML Page Routes ---
@app.get("/")
def serve_home():
    return FileResponse(os.path.join(FRONTEND_DIR, "demo.html"))


@app.get("/demo.html")
def serve_demo():
    return FileResponse(os.path.join(FRONTEND_DIR, "demo.html"))


@app.get("/login.html")
def serve_login():
    return FileResponse(os.path.join(FRONTEND_DIR, "login.html"))


@app.get("/create.html")
def serve_create():
    return FileResponse(os.path.join(FRONTEND_DIR, "create.html"))