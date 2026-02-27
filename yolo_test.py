import os
import json
from ultralytics import YOLO

# ==========================================
# 1. 前置检查与加载外部 JSON 字典
# ==========================================
json_path = 'ingredients_dict.json'
image_path = 'test_food.jpg'

if not os.path.exists(json_path):
    print(f"❌ 错误：找不到外部字典 '{json_path}'！")
    exit()

if not os.path.exists(image_path):
    print(f"❌ 错误：找不到测试图片 '{image_path}'！")
    exit()

# 读取 JSON 文件
print("⏳ 正在读取外部食材字典...")
with open(json_path, 'r', encoding='utf-8') as f:
    ingredient_data = json.load(f)

# 解析字典：YOLO只需要英文列表，但我们还需要一个反查表用来找中文
yolo_classes_en = []  # 给 YOLO 用的单纯英文列表 (例: ['tomato', 'potato', ...])
mapping_dict = {}  # 反查表 (例: {'tomato': {'zh': '番茄', 'category': 'vegetables'}})

for category, items in ingredient_data.items():
    for item in items:
        en_name = item['en']
        zh_name = item['zh']

        yolo_classes_en.append(en_name)
        mapping_dict[en_name] = {
            "zh": zh_name,
            "category": category
        }

print(f"📚 成功从 JSON 中提取了 {len(yolo_classes_en)} 种食材！")

# ==========================================
# 2. 初始化 YOLO 并注入词表
# ==========================================
print("⏳ 正在加载 YOLO-World 模型...")
model = YOLO('yolov8s-world.pt')

# 把刚刚提取的全部英文单词喂给模型
model.set_classes(yolo_classes_en)

# ==========================================
# 3. 开始识别
# ==========================================
print(f"🔍 正在识别图片: {image_path} ...")
results = model.predict(image_path, conf=0.15)

# ==========================================
# 4. 解析结果并组装成前端需要的【多语言嵌套格式】
# ==========================================
print("\n" + "=" * 50)
print("🎯 最终组装的 API 数据结构：")

final_response = {
    "detected_ingredients": []
}

for box in results[0].boxes:
    class_id = int(box.cls[0])  # YOLO 返回的索引 (比如 0)
    en_name = yolo_classes_en[class_id]  # 根据索引找到英文名 (比如 'tomato')

    # 【核心逻辑】用英文名去反查表里找详细信息
    detail_info = mapping_dict[en_name]

    # 组装成你需求文档里前端要的格式！
    item_data = {
        "name": {
            "zh": detail_info["zh"],
            "zh_Hant": detail_info["zh"],  # 繁体暂时用简体代替，以后可加 opencc 转换
            "en": en_name.capitalize()
        },
        "category": detail_info["category"],
        "confidence": round(float(box.conf[0]), 3),
        "bbox": [round(x, 1) for x in box.xyxy[0].tolist()]
    }

    final_response["detected_ingredients"].append(item_data)

# 漂亮地打印出最终的 JSON 数据
print(json.dumps(final_response, indent=2, ensure_ascii=False))
print("=" * 50)

# 保存画框图片看效果
output_img = "output_food.jpg"
results[0].save(output_img)
print(f"\n🖼️ 已经生成带框的识别图：{output_img}")