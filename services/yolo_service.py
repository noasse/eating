import os
import json
import io
from PIL import Image
from ultralytics import YOLO


class YoloService:
    def __init__(self):
        print("[YOLO Service] initialization models and diction...")

        # load diction
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from config import INGREDIENTS_JSON_PATH, YOLO_MODEL_PATH
        with open(INGREDIENTS_JSON_PATH, 'r', encoding='utf-8') as f:
            ingredient_data = json.load(f)

        self.yolo_classes_en = []
        self.mapping_dict = {}

        for category, items in ingredient_data.items():
            for item in items:
                en_name = item['en']
                self.yolo_classes_en.append(en_name)
                self.mapping_dict[en_name] = {
                    "zh": item['zh'],
                    "category": category
                }

        # load model and inject the glossary
        self.model = YOLO(YOLO_MODEL_PATH)
        self.model.set_classes(self.yolo_classes_en)

        print(f"[YOLO Service] initialization completed，loaded {len(self.yolo_classes_en)} kind of ingredients.")

    def identify(self, image_bytes: bytes):
        """receive the image byte stream and return the identified JSON list"""
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        results = self.model.predict(image, conf=0.15)

        detected_ingredients = []
        for box in results[0].boxes:
            class_id = int(box.cls[0])
            en_name = self.yolo_classes_en[class_id]
            detail_info = self.mapping_dict[en_name]

            # Chinese and English
            item_data = {
                "name": {
                    "zh": detail_info["zh"],
                    "en": en_name.capitalize()
                },
                "category": detail_info["category"],
                "confidence": round(float(box.conf[0]), 3),
                "bbox": [round(x, 1) for x in box.xyxy[0].tolist()]
            }
            detected_ingredients.append(item_data)

        return detected_ingredients


yolo_app = YoloService()