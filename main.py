import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.ingredients import router as ingredients_router
from api.recipes import router as recipes_router
from api.auth import router as auth_router
from api.users import router as users_router
from models import create_all_tables

app = FastAPI(title="吃啥 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_all_tables()

app.include_router(ingredients_router, prefix="/api")
app.include_router(recipes_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_excludes=[".venv/*", "*.pyc", "__pycache__/*"],
    )
