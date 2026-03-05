from database import Base, engine
from models.user import User
from models.allergen import Allergen
from models.favorite import Favorite

def create_all_tables():
    Base.metadata.create_all(bind=engine)

__all__ = ["User", "Allergen", "Favorite", "create_all_tables"]
