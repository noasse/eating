from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from services.llm_service import llm_app

router = APIRouter()


def ok(data):
    return {"code": 200, "message": "success", "data": data}


def err(code: int, message: str):
    return {"code": code, "message": message, "data": None}


class GenerateRequest(BaseModel):
    diners: int
    ingredients: List[str]
    dietary: Optional[List[str]] = []
    allergens: Optional[List[str]] = []
    preferences: Optional[List[str]] = []


@router.post("/recipes/generate")
def generate_recipes(req: GenerateRequest):
    """Call Qwen to generate recipes based on ingredients and dining information"""
    try:
        result = llm_app.generate_menu(
            diners=req.diners,
            ingredients=req.ingredients,
            dietary=req.dietary,
            allergens=req.allergens,
            preferences=req.preferences,
        )
    except RuntimeError as e:
        return err(500, str(e))

    return ok(result)


@router.get("/categories")
def get_categories():
    """Return the list of recipe categories"""
    categories = [
        {"id": "breakfast", "name": {"zh": "早餐", "en": "Breakfast"}},
        {"id": "lunch",     "name": {"zh": "午餐", "en": "Lunch"}},
        {"id": "dinner",    "name": {"zh": "晚餐", "en": "Dinner"}},
        {"id": "quick",     "name": {"zh": "快手菜", "en": "Quick Meal"}},
        {"id": "healthy",   "name": {"zh": "健康轻食", "en": "Healthy"}},
        {"id": "spicy",     "name": {"zh": "麻辣重口", "en": "Spicy"}},
    ]
    return ok({"categories": categories})


@router.get("/recipes/search")
def search_recipes(
    keyword: str = "",
    page: int = 1,
    page_size: int = 10,
):
    """搜索菜谱 - TODO: 接入数据库后实现"""
    return ok({"recipes": [], "total": 0, "page": page, "page_size": page_size})


@router.get("/recipes/recommend")
def recommend_recipes(
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
):
    """推荐菜谱 - TODO: 接入数据库后实现"""
    return ok({"recipes": [], "total": 0, "page": page, "page_size": page_size})


@router.get("/recipes/{recipe_id}")
def get_recipe(recipe_id: str):
    """获取菜谱详情 - TODO: 接入数据库后实现"""
    return ok(None)
