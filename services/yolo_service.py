# 文件路径: services/yolo_service.py
import os
import json
import io
from PIL import Image
from ultralytics import YOLO


class YoloService:
    def __init__(self):
        print("⏳ [YOLO Service] 正在初始化模型和字典...")

        # 1. 加载字典 (注意路径指向 data 文件夹)
        json_path = os.path.join(os.path.dirname(__file__), '../data/ingredients_dict.json')
        with open(json_path, 'r', encoding='utf-8') as f:
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

        # 2. 加载模型并注入词汇表
        model_path = os.path.join(os.path.dirname(__file__), '../data/yolov8s-world.pt')
        self.model = YOLO(model_path)
        self.model.set_classes(self.yolo_classes_en)

        print(f"✅ [YOLO Service] 初始化完成，已加载 {len(self.yolo_classes_en)} 种食材。")

    def identify(self, image_bytes: bytes):
        """核心业务逻辑：接收图片字节流，返回识别出来的 JSON 列表"""
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        results = self.model.predict(image, conf=0.15)

        detected_ingredients = []
        for box in results[0].boxes:
            class_id = int(box.cls[0])
            en_name = self.yolo_classes_en[class_id]
            detail_info = self.mapping_dict[en_name]

            item_data = {
                "name": {
                    "zh": detail_info["zh"],
                    "zh_Hant": detail_info["zh"],
                    "en": en_name.capitalize()
                },
                "category": detail_info["category"],
                "confidence": round(float(box.conf[0]), 3),
                "bbox": [round(x, 1) for x in box.xyxy[0].tolist()]
            }
            detected_ingredients.append(item_data)

        return detected_ingredients


# 实例化一个单例供外部调用
yolo_app = YoloService()