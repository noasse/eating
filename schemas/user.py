from pydantic import BaseModel
from datetime import datetime
from typing import Any


class AllergenCreate(BaseModel):
    name: str


class AllergenOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class FavoriteCreate(BaseModel):
    recipe_name: str
    recipe_data: dict[str, Any]


class FavoriteOut(BaseModel):
    id: int
    recipe_name: str
    recipe_data: dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True
