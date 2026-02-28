import requests
import json
import time
import re


# ==========================================
# 0. 🛠️ 核心工具：从大模型的废话中抠出纯净的 JSON
# ==========================================
def extract_json_from_text(text):
    """无论大模型说多少废话，只提取它输出的 JSON 部分"""
    # 尝试匹配 markdown 格式的 ```json ... ```
    match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
    if match:
        return match.group(1)

    # 如果没用 markdown，直接找第一个 { 和最后一个 }
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        return text[start:end + 1]

    # 实在找不到，就原样返回，让后续的 json.loads 报错
    return text


# ==========================================
# 1. 测试用例
# ==========================================
test_cases = [
    {
        "name": "1. 苦逼打工人 (1人)",
        "ingredients": ["番茄", "鸡蛋", "猪肉"],
        "diners": 1,
        "dietary": [],
        "allergens": [],
        "preferences": ["快手", "下饭"]
    },
    {
        "name": "2. 情侣约会 (2人)",
        "ingredients": ["牛肉", "土豆", "西兰花", "虾"],
        "diners": 2,
        "dietary": ["减脂"],
        "allergens": ["海鲜"],
        "preferences": ["清淡"]
    },
    {
        "name": "3. 宿舍聚餐 (4人)",
        "ingredients": ["鸡肉", "豆腐", "白菜", "鱼", "茄子", "排骨"],
        "diners": 4,
        "dietary": ["不吃香菜"],
        "allergens": ["花生"],
        "preferences": ["重口味", "麻辣"]
    }
]


# ==========================================
# 2. 核心 Prompt
# ==========================================
def get_prompt(case):
    return f"""
你是一个顶级的国际米其林 AI 厨师长。
请根据以下就餐情况，自主决定应该做几道菜（通常 N 个人需要 N 到 N+1 道菜的组合），并规划出一桌完美的菜单。

【当前就餐情况】
- 就餐人数: {case['diners']} 人
- 现有食材: {case['ingredients']}
- 个人忌口: {case['dietary']} (绝对遵守)
- 致死过敏原: {case['allergens']} (必须坚决丢弃或替换危险食材)
- 口味偏好: {case['preferences']}

【输出格式要求】
你必须输出一个完整的 JSON。可以包含 markdown 标记。格式如下：
{{
  "reasoning": "你的分析过程",
  "planned_dish_count": 0, 
  "recipes": [
    {{
      "name": {{"zh": "菜名", "en": "Name"}},
      "description": {{"zh": "描述", "en": "Description"}},
      "category": {{"zh": "热菜", "en": "Category"}},
      "difficulty": {{"zh": "简单", "en": "Easy"}},
      "calories": 250,
      "cooking_time": 15,
      "servings": {case['diners']}, 
      "ingredients": [
        {{"name": {{"zh": "食材名", "en": "Ingredient"}}, "quantity": "数量", "unit": {{"zh": "单位", "en": "Unit"}}}}
      ],
      "steps": [
        {{"step": 1, "description": {{"zh": "步骤", "en": "Step"}}}}
      ],
      "tips": {{"zh": "小贴士", "en": "Tips"}},
      "tags": [{{"zh": "标签", "en": "Tag"}}]
    }}
  ]
}}
"""


# ==========================================
# 3. 自动化测试引擎
# ==========================================
def run_tests():
    print(f"🚀 开始进行 14B 模型自主规划菜单测试 (已解除限制，自由发挥版)...\n")

    for case in test_cases:
        print(f"▶️ 正在测试: {case['name']}")
        prompt = get_prompt(case)

        payload = {
            "model": "qwen3:14b",  # 确保名字对得上
            "prompt": prompt,
            "stream": False,
            # ⛔️ 删除了 "format": "json"！把自由还给大模型！
            "options": {
                "temperature": 0.7,
                "num_ctx": 8192,
                "num_predict": 8192
            }
        }

        try:
            start_time = time.time()
            res = requests.post("http://localhost:11434/api/generate", json=payload)
            res.raise_for_status()

            # 1. 拿到原始的废话连篇的文本
            raw_text = res.json().get("response", "").strip()

            # 2. 🛠️ 用提取工具，把 JSON 抠出来
            pure_json_str = extract_json_from_text(raw_text)

            # 3. 解析纯净的 JSON
            data = json.loads(pure_json_str)
            cost = time.time() - start_time

            recipes_list = data.get("recipes", [])
            actual_count = len(recipes_list)
            planned_count = data.get("planned_dish_count", 0)
            reasoning = data.get('reasoning', '无')

            print(f"  ✅ 测试通过！(耗时 {cost:.1f}秒)")
            print(f"  🧠 AI 思考过程:\n     {reasoning}")
            print(f"  📊 AI 决定做 {planned_count} 道菜 (实际生成 {actual_count} 道)：")

            for idx, recipe in enumerate(recipes_list):
                dish_zh = recipe.get('name', {}).get('zh', '未知菜名')
                print(f"     🍲 第 {idx + 1} 道: {dish_zh}")

        except json.JSONDecodeError as e:
            print(f"  ❌ JSON解析失败！大模型格式依然不对。")
            print(f"  [原始文本]: \n{raw_text[:500]}...")
        except Exception as e:
            print(f"  ❌ 错误: {e}")

        print("-" * 60)


if __name__ == "__main__":
    run_tests()