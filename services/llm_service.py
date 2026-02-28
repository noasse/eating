import requests
import json
import re


class LLMService:
    def __init__(self):
        # Model parameters
        self.model_name = "qwen3:14b"
        self.api_url = "http://localhost:11434/api/generate"
        print(f"[LLM Service] initialization completed，the local model has been mounted: {self.model_name}")

    def _extract_json_from_text(self, text: str) -> str:
        """clearly JSON"""
        match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            return match.group(1)
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            return text[start:end + 1]
        return text

    def generate_menu(self, diners: int, ingredients: list, dietary: list = None, allergens: list = None,
                      preferences: list = None):
        """
        core business logic: receive parameters, generate menu JSON data
        """
        dietary = dietary or []
        allergens = allergens or []
        preferences = preferences or []

        # Prompt
        prompt = f"""
你是一个顶级的国际米其林 AI 厨师长。
请根据以下就餐情况，自主决定应该做几道菜（通常 N 个人需要 N 到 N+1 道菜的组合），并规划出一桌完美的菜单。

【当前就餐情况】
- 就餐人数: {diners} 人
- 现有食材: {ingredients}
- 个人忌口: {dietary} (绝对遵守)
- 致死过敏原: {allergens} (必须坚决丢弃或替换危险食材)
- 口味偏好: {preferences}

【输出格式要求】
你必须输出一个完整的 JSON。格式如下：
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
      "servings": {diners}, 
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
        # Assemble the request body
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_ctx": 8192,
                "num_predict": 8192  # prevent cut off if it is too long
            }
        }

        try:
            # request to ollama, limit 3 mins
            res = requests.post(self.api_url, json=payload, timeout=180)
            res.raise_for_status()

            raw_text = res.json().get("response", "")

            # clean and analyze JSON
            pure_json_str = self._extract_json_from_text(raw_text)
            data = json.loads(pure_json_str)

            return data

        except Exception as e:
            # If it fails or times out, throw exception out to caller
            raise RuntimeError(f"大模型生成菜单失败: {str(e)}")


llm_app = LLMService()