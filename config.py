import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

INGREDIENTS_JSON_PATH = os.path.join(DATA_DIR, "ingredients_dict.json")
YOLO_MODEL_PATH = os.path.join(DATA_DIR, "yolov8s-world.pt")

OLLAMA_URL = "http://localhost:11434/api/generate"
LLM_MODEL = "qwen3:14b"
