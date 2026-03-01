import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User, Allergen, Favorite
from schemas.user import AllergenCreate, AllergenOut, FavoriteCreate, FavoriteOut
from services.auth_service import get_current_user_id

router = APIRouter()


def ok(data):
    return {"code": 200, "message": "success", "data": data}


def err(code: int, message: str):
    return {"code": code, "message": message, "data": None}


@router.get("/users/me")
def get_me(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Get currently logged-in user information"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return err(404, "用户不存在")
    return ok({"id": user.id, "username": user.username, "email": user.email})


# ── 过敏原 ──────────────────────────────────────────────


@router.get("/users/allergens")
def list_allergens(
    user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)
):
    """Get the current user's allergen list"""
    items = db.query(Allergen).filter(Allergen.user_id == user_id).all()
    return ok({"allergens": [AllergenOut.model_validate(i).model_dump() for i in items]})


@router.post("/users/allergens")
def add_allergen(
    req: AllergenCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Add allergen"""
    allergen = Allergen(user_id=user_id, name=req.name)
    db.add(allergen)
    db.commit()
    db.refresh(allergen)
    return ok(AllergenOut.model_validate(allergen).model_dump())


@router.delete("/users/allergens/{allergen_id}")
def delete_allergen(
    allergen_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Delete allergen"""
    allergen = (
        db.query(Allergen)
        .filter(Allergen.id == allergen_id, Allergen.user_id == user_id)
        .first()
    )
    if not allergen:
        return err(404, "过敏原不存在")
    db.delete(allergen)
    db.commit()
    return ok(None)




@router.get("/users/favorites")
def list_favorites(
    user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)
):
    """Get the current user's favorites list"""
    items = db.query(Favorite).filter(Favorite.user_id == user_id).all()
    result = []
    for item in items:
        result.append({
            "id": item.id,
            "recipe_name": item.recipe_name,
            "recipe_data": json.loads(item.recipe_data),
            "created_at": item.created_at.isoformat(),
        })
    return ok({"favorites": result})


@router.post("/users/favorites")
def add_favorite(
    req: FavoriteCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Save a recipe"""
    favorite = Favorite(
        user_id=user_id,
        recipe_name=req.recipe_name,
        recipe_data=json.dumps(req.recipe_data, ensure_ascii=False),
    )
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return ok({
        "id": favorite.id,
        "recipe_name": favorite.recipe_name,
        "recipe_data": req.recipe_data,
        "created_at": favorite.created_at.isoformat(),
    })


@router.delete("/users/favorites/{favorite_id}")
def delete_favorite(
    favorite_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """cancel save"""
    favorite = (
        db.query(Favorite)
        .filter(Favorite.id == favorite_id, Favorite.user_id == user_id)
        .first()
    )
    if not favorite:
        return err(404, "收藏不存在")
    db.delete(favorite)
    db.commit()
    return ok(None)
