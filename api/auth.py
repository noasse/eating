from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from services.auth_service import hash_password, verify_password, create_token

router = APIRouter()


def ok(data):
    return {"code": 200, "message": "success", "data": data}


def err(code: int, message: str):
    return {"code": code, "message": message, "data": None}


@router.post("/auth/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Successful registration of new users token will be returned"""
    if db.query(User).filter(User.username == req.username).first():
        return err(400, "用户名已存在")
    if db.query(User).filter(User.email == req.email).first():
        return err(400, "邮箱已被注册")

    user = User(
        username=req.username,
        email=req.email,
        hashed_password=hash_password(req.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token(user.id, user.username)
    return ok(TokenResponse(access_token=token, username=user.username).model_dump())


@router.post("/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Log in with username and password, token will be returned"""
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.hashed_password):
        return err(401, "用户名或密码错误")

    token = create_token(user.id, user.username)
    return ok(TokenResponse(access_token=token, username=user.username).model_dump())
