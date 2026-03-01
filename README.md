# 吃啥 APP — 后端服务 / EatWhat APP — Backend Service

> YOLO 食材识别 + Qwen 大模型菜谱生成
> YOLO Ingredient Recognition + Qwen LLM Recipe Generation

---

## 目录 / Table of Contents

- [项目简介 / Overview](#项目简介--overview)
- [技术栈 / Tech Stack](#技术栈--tech-stack)
- [项目结构 / Project Structure](#项目结构--project-structure)
- [快速开始 / Quick Start](#快速开始--quick-start)
- [接口文档 / API Reference](#接口文档--api-reference)
- [接口测试 / Testing](#接口测试--testing)

---

## 项目简介 / Overview

**中文**
用户拍照上传食材图片，后端通过 YOLO-World 模型识别食材，再将识别结果传给本地 Qwen 大模型，生成个性化菜谱（支持人数、忌口、过敏原、口味偏好）。

**English**
Users upload a photo of their ingredients. The backend uses YOLO-World to detect what ingredients are present, then passes the results to a local Qwen LLM to generate personalized recipes based on number of diners, dietary restrictions, allergens, and taste preferences.

---

## 技术栈 / Tech Stack

| 组件 / Component | 技术 / Technology |
|---|---|
| Web 框架 / Web Framework | FastAPI |
| YOLO 模型 / YOLO Model | YOLOv8s-World (ultralytics) |
| 大模型 / LLM | Qwen3:14b (via Ollama) |
| 语言支持 / Language | 中文 / English |

---

## 项目结构 / Project Structure

```
eating/
├── main.py                  # FastAPI 入口 / Entry point
├── config.py                # 统一配置 / Unified config
├── requirements.txt         # 依赖清单 / Dependencies
├── api/
│   ├── ingredients.py       # 食材接口 / Ingredient APIs
│   └── recipes.py           # 菜谱接口 / Recipe APIs
├── models/
│   └── __init__.py          # 数据库占位 / DB placeholder (TODO)
├── services/
│   ├── yolo_service.py      # YOLO 识别服务 / YOLO recognition
│   └── llm_service.py       # LLM 菜谱生成 / LLM recipe generation
└── data/
    ├── ingredients_dict.json # 食材中英文字典 / Bilingual ingredient dict
    └── yolov8s-world.pt      # YOLO 模型权重 / YOLO model weights
```

---

## 快速开始 / Quick Start

### 前置条件 / Prerequisites

1. **Python 3.12+**
2. **Ollama** 已安装并运行，且已拉取 Qwen 模型：
   ```bash
   ollama pull qwen3:14b
   ollama serve
   ```

### 安装依赖 / Install Dependencies

```bash
pip install -r requirements.txt
```

### 启动服务 / Start Server

```bash
python main.py
```

服务启动后访问 / After startup, visit:
- **API 文档 / Docs**: http://localhost:8000/docs
- **服务地址 / Base URL**: http://localhost:8000

> 首次启动会加载 YOLO 模型，约需 10 秒。
> First startup loads the YOLO model, takes ~10 seconds.

---

## 接口文档 / API Reference

所有接口统一返回格式 / Unified response format:

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

---

### 1. 识别食材 / Recognize Ingredients

**`POST /api/ingredients/recognize`**

上传图片，返回 YOLO 识别出的食材列表。
Upload an image, returns a list of detected ingredients.

**Request**
```
Content-Type: multipart/form-data
Field: image (file)
```

**Response**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "detected_ingredients": [
      {
        "name": { "zh": "番茄/西红柿", "en": "Tomato" },
        "category": "vegetables",
        "confidence": 0.748,
        "bbox": [440.5, 344.6, 552.9, 449.4]
      }
    ]
  }
}
```

---

### 2. 获取全部食材列表 / List All Ingredients

**`GET /api/ingredients`**

返回字典中全部 128 种可识别食材。
Returns all 128 recognizable ingredients from the dictionary.

**Response**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "ingredients": [
      {
        "name": { "zh": "番茄/西红柿", "en": "Tomato" },
        "category": "vegetables"
      }
    ]
  }
}
```

---

### 3. 生成菜谱 / Generate Recipes

**`POST /api/recipes/generate`**

根据食材和就餐信息，调用 Qwen 生成完整菜谱。
Calls Qwen to generate a full recipe plan based on ingredients and dining info.

> ⚠️ 本接口调用本地大模型，响应时间约 30–120 秒。
> ⚠️ This endpoint calls a local LLM. Response time is ~30–120 seconds.

**Request Body**
```json
{
  "diners": 2,
  "ingredients": ["番茄", "鸡蛋", "土豆"],
  "dietary": ["不吃香菜"],
  "allergens": ["花生"],
  "preferences": ["快手", "下饭"]
}
```

| 字段 / Field | 类型 / Type | 必填 / Required | 说明 / Description |
|---|---|---|---|
| `diners` | int | ✅ | 就餐人数 / Number of diners |
| `ingredients` | string[] | ✅ | 食材列表 / Ingredient list |
| `dietary` | string[] | ❌ | 忌口 / Dietary restrictions |
| `allergens` | string[] | ❌ | 过敏原 / Allergens to avoid |
| `preferences` | string[] | ❌ | 口味偏好 / Taste preferences |

**Response**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "reasoning": "根据2人就餐设计两道快手菜...",
    "planned_dish_count": 2,
    "recipes": [
      {
        "name": { "zh": "番茄炒蛋", "en": "Tomato Stir-Fried Eggs" },
        "description": { "zh": "经典家常菜", "en": "Classic home-style dish" },
        "category": { "zh": "热菜", "en": "Main Course" },
        "difficulty": { "zh": "简单", "en": "Easy" },
        "calories": 220,
        "cooking_time": 15,
        "servings": 2,
        "ingredients": [
          {
            "name": { "zh": "番茄", "en": "Tomato" },
            "quantity": "2个",
            "unit": { "zh": "个", "en": "Pieces" }
          }
        ],
        "steps": [
          {
            "step": 1,
            "description": { "zh": "番茄切块，鸡蛋打散备用", "en": "Dice tomatoes and beat eggs" }
          }
        ],
        "tips": { "zh": "炒蛋时加少许盐可让蛋更嫩滑", "en": "Add a pinch of salt when cooking eggs" },
        "tags": [
          { "zh": "快手菜", "en": "Quick Meal" }
        ]
      }
    ]
  }
}
```

---

### 4. 获取菜谱分类 / Get Categories

**`GET /api/categories`**

**Response**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "categories": [
      { "id": "breakfast", "name": { "zh": "早餐", "en": "Breakfast" } },
      { "id": "lunch",     "name": { "zh": "午餐", "en": "Lunch" } },
      { "id": "dinner",    "name": { "zh": "晚餐", "en": "Dinner" } },
      { "id": "quick",     "name": { "zh": "快手菜", "en": "Quick Meal" } },
      { "id": "healthy",   "name": { "zh": "健康轻食", "en": "Healthy" } },
      { "id": "spicy",     "name": { "zh": "麻辣重口", "en": "Spicy" } }
    ]
  }
}
```

---

### 5. 占位接口 / Placeholder Endpoints (TODO: 接入数据库)

以下接口路由和参数已就位，待数据库接入后实现业务逻辑。
Routes and parameters are in place. Business logic will be filled in after DB integration.

| 接口 / Endpoint | 方法 / Method | 说明 / Description |
|---|---|---|
| `/api/recipes/search` | GET | 搜索菜谱 / Search recipes |
| `/api/recipes/recommend` | GET | 推荐菜谱 / Recommend recipes |
| `/api/recipes/{recipe_id}` | GET | 菜谱详情 / Recipe detail |

---

## 接口测试 / Testing

### 方式一：Swagger UI（推荐 / Recommended）

启动服务后访问 http://localhost:8000/docs，可在浏览器直接调试所有接口。
After starting the server, visit http://localhost:8000/docs to test all endpoints in the browser.

### 方式二：curl 命令行 / curl Command Line

```bash
# 1. 获取分类
curl http://localhost:8000/api/categories

# 2. 获取食材列表
curl http://localhost:8000/api/ingredients

# 3. 上传图片识别食材
curl -X POST http://localhost:8000/api/ingredients/recognize \
  -F "image=@/path/to/your/photo.jpg"

# 4. 生成菜谱
curl -X POST http://localhost:8000/api/recipes/generate \
  -H "Content-Type: application/json" \
  -d '{
    "diners": 2,
    "ingredients": ["番茄", "鸡蛋"],
    "allergens": [],
    "preferences": ["快手"]
  }'
```
