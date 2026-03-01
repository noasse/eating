# 吃啥 APP — 后端服务 / EatWhat APP — Backend Service

> YOLO 食材识别 + Qwen 大模型菜谱生成 + 用户登录系统
> YOLO Ingredient Recognition + Qwen LLM Recipe Generation + User Auth

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
用户拍照上传食材图片，后端通过 YOLO-World 模型识别食材，再将识别结果传给本地 Qwen 大模型，生成个性化菜谱（支持人数、忌口、过敏原、口味偏好）。用户可注册/登录，收藏菜谱，保存个人过敏原。

**English**
Users upload a photo of their ingredients. The backend uses YOLO-World to detect what ingredients are present, then passes the results to a local Qwen LLM to generate personalized recipes. Users can register/login, save favorites, and manage allergens.

---

## 技术栈 / Tech Stack

| 组件 / Component | 技术 / Technology |
|---|---|
| Web 框架 / Web Framework | FastAPI |
| YOLO 模型 / YOLO Model | YOLOv8s-World (ultralytics) |
| 大模型 / LLM | Qwen3:14b (via Ollama) |
| 数据库 / Database | PostgreSQL + SQLAlchemy |
| 认证 / Auth | JWT (python-jose + passlib) |
| 语言支持 / Language | 中文 / English |

---

## 项目结构 / Project Structure

```
eatfor/
├── main.py                  # FastAPI 入口 / Entry point
├── config.py                # 统一配置 / Unified config
├── database.py              # DB 连接和 Session / DB connection (由 DB 负责人实现)
├── requirements.txt         # 依赖清单 / Dependencies
├── .env                     # 环境变量 / Env vars (不提交 git)
├── api/
│   ├── ingredients.py       # 食材接口 / Ingredient APIs
│   ├── recipes.py           # 菜谱接口 / Recipe APIs
│   ├── auth.py              # 注册/登录 / Auth APIs
│   └── users.py             # 用户/收藏/过敏原 / User APIs
├── models/
│   ├── user.py              # User ORM 模型 (由 DB 负责人实现)
│   ├── allergen.py          # Allergen ORM 模型 (由 DB 负责人实现)
│   └── favorite.py          # Favorite ORM 模型 (由 DB 负责人实现)
├── schemas/
│   ├── auth.py              # 注册/登录 Pydantic 模型
│   └── user.py              # 用户/收藏/过敏原 Pydantic 模型
├── services/
│   ├── yolo_service.py      # YOLO 识别服务 / YOLO recognition
│   ├── llm_service.py       # LLM 菜谱生成 / LLM recipe generation
│   └── auth_service.py      # JWT / 密码处理 / JWT & password
└── data/
    ├── ingredients_dict.json # 食材中英文字典 / Bilingual ingredient dict
    └── yolov8s-world.pt      # YOLO 模型权重 / YOLO model weights
```

---

## 快速开始 / Quick Start

### 前置条件 / Prerequisites

1. **Python 3.12+**
2. **PostgreSQL** 已安装并运行，创建数据库 `eatfor`
3. **Ollama** 已安装并运行，且已拉取 Qwen 模型：
   ```bash
   ollama pull qwen3:14b
   ollama serve
   ```

### 配置环境变量 / Configure Env

复制并填写 `.env` 文件（不提交到 git）：
```
DATABASE_URL=postgresql://用户名:密码@localhost:5432/eatfor
JWT_SECRET=随机字符串（越长越安全）
```

### 安装依赖 / Install Dependencies

```bash
pip install -r requirements.txt
```

### 启动服务 / Start Server

```bash
python main.py
```

服务启动时会自动建表。启动后访问 / After startup, visit:
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

需要登录的接口须在 Header 中携带 / Protected endpoints require:
```
Authorization: Bearer <access_token>
```

---

### 认证接口 / Auth

#### 注册 / Register

**`POST /api/auth/register`**

**Request Body**
```json
{
  "username": "张三",
  "email": "zhangsan@example.com",
  "password": "你的密码"
}
```

**Response**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "access_token": "eyJ...",
    "token_type": "bearer",
    "username": "张三"
  }
}
```

---

#### 登录 / Login

**`POST /api/auth/login`**

**Request Body**
```json
{
  "username": "张三",
  "password": "你的密码"
}
```

**Response**（同注册）

---

### 用户接口 / User（需要登录 / Requires Auth）

#### 获取当前用户信息

**`GET /api/users/me`**

**Response**
```json
{
  "code": 200,
  "message": "success",
  "data": { "id": 1, "username": "张三", "email": "zhangsan@example.com" }
}
```

---

#### 过敏原管理 / Allergens

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/users/allergens` | 获取过敏原列表 |
| POST | `/api/users/allergens` | 添加过敏原，body: `{"name": "花生"}` |
| DELETE | `/api/users/allergens/{id}` | 删除过敏原 |

**GET Response**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "allergens": [
      { "id": 1, "name": "花生" }
    ]
  }
}
```

---

#### 收藏菜谱 / Favorites

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/users/favorites` | 获取收藏列表 |
| POST | `/api/users/favorites` | 收藏一道菜谱 |
| DELETE | `/api/users/favorites/{id}` | 取消收藏 |

**POST Request Body**
```json
{
  "recipe_name": "番茄炒蛋",
  "recipe_data": { ...单道菜谱 JSON... }
}
```

**GET Response**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "favorites": [
      {
        "id": 1,
        "recipe_name": "番茄炒蛋",
        "recipe_data": { ... },
        "created_at": "2026-03-01T12:00:00"
      }
    ]
  }
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

| 接口 / Endpoint | 方法 / Method | 说明 / Description |
|---|---|---|
| `/api/recipes/search` | GET | 搜索菜谱 / Search recipes |
| `/api/recipes/recommend` | GET | 推荐菜谱 / Recommend recipes |
| `/api/recipes/{recipe_id}` | GET | 菜谱详情 / Recipe detail |

---

## 接口测试 / Testing

### 方式一：Swagger UI（推荐 / Recommended）

启动服务后访问 http://localhost:8000/docs。
测试需要登录的接口时，点击右上角 **Authorize** 按钮，填入 `Bearer <你的token>`。

### 方式二：curl 命令行 / curl Command Line

```bash
# 注册
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"123456"}'

# 登录（拿 token）
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"123456"}'

# 获取用户信息（替换 TOKEN）
curl http://localhost:8000/api/users/me \
  -H "Authorization: Bearer TOKEN"

# 添加过敏原
curl -X POST http://localhost:8000/api/users/allergens \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"花生"}'

# 收藏菜谱
curl -X POST http://localhost:8000/api/users/favorites \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"recipe_name":"番茄炒蛋","recipe_data":{"name":"番茄炒蛋"}}'

# 识别食材
curl -X POST http://localhost:8000/api/ingredients/recognize \
  -F "image=@/path/to/your/photo.jpg"

# 生成菜谱
curl -X POST http://localhost:8000/api/recipes/generate \
  -H "Content-Type: application/json" \
  -d '{"diners":2,"ingredients":["番茄","鸡蛋"],"allergens":[],"preferences":["快手"]}'
```
