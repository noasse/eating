import json
from fastapi import APIRouter, UploadFile, File, HTTPException
from services.yolo_service import yolo_app
from config import INGREDIENTS_JSON_PATH

router = APIRouter()


def ok(data):
    return {"code": 200, "message": "success", "data": data}


def err(code: int, message: str):
    return {"code": code, "message": message, "data": None}


@router.post("/ingredients/recognize")
async def recognize_ingredients(image: UploadFile = File(...)):
    """上传图片，返回 YOLO 识别出的食材列表"""
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="请上传图片文件")

    image_bytes = await image.read()
    try:
        detected = yolo_app.identify(image_bytes)
    except Exception as e:
        return err(500, f"识别失败: {str(e)}")

    return ok({"detected_ingredients": detected})


@router.get("/ingredients")
def list_ingredients():
    """返回全部可识别食材列表"""
    with open(INGREDIENTS_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = []
    for category, items in data.items():
        for item in items:
            result.append({
                "name": {"zh": item["zh"], "en": item["en"].capitalize()},
                "category": category
            })

    return ok({"ingredients": result})
