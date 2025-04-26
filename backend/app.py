# backend/app.py
from __future__ import annotations

import os
import base64
import mimetypes
from io import BytesIO
from pathlib import Path
import json
import re

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import openai                     # openai>=1.0.0
from PIL import Image

# ───────────────────────────────────────────────
# 環境変数の読み込み (.env から OPENAI_API_KEY を取得)
# ───────────────────────────────────────────────
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY が設定されていません。")

# OpenAI クライアントを初期化
client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)

# ───────────────────────────────────────────────
# FastAPI アプリ設定
# ───────────────────────────────────────────────
app = FastAPI(
    title="Chat Backend",
    description="Next.js フロントエンドと連携するシンプルなチャット API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # フロントエンドのURL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ───────────────────────────────────────────────
# リクエスト／レスポンスモデル
# ───────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, example="こんにちは！")

class ChatResponse(BaseModel):
    reply: str

class DishAnalysisResponse(BaseModel):
    dish_name: str
    ingredients: list[str]

class IngredientInfo(BaseModel):
    食材の名前: str
    食材の育った環境: str
    食材の豆知識: str

class IngredientList(BaseModel):
    ingredients: list[str]

# ───────────────────────────────────────────────
# 原材料リストの取得
# ───────────────────────────────────────────────
ingredient_list = [
 # Grains & Carbohydrates
 "Rice", "Bread", "Wheat", "Potato", "Sweet potato", "Corn",
 # Vegetables
 "Cabbage", "Lettuce", "Chinese Cabbage", "Spinach", "Japanese Mustard Spinach", "Daikon Radish", "Carrot", "Burdock Root", "Lotus Root", "Tomato", "Cucumber", "Eggplant", "Green Pepper", "Paprika", "Pumpkin", "Onion", "Green Onion", "Garlic", "Broccoli", "Cauliflower", "Asparagus", "Mushrooms",
 # Fruits
 "Apple", "Orange", "Banana", "Strawberry", "Grape", "Peach", "Kiwi", "Lemon",
# Meats
 "Chicken", "Pork", "Beef",
 # Seafood
 "Salmon", "Tuna", "Mackerel", "Shrimp", "Crab", "Squid", "Octopus",
 # Legumes & Nuts
"Soybeans",
 # Dairy
"Milk", "Cheese", "Yogurt",
 # Eggs
 "Egg",
 # Herbs & Spices
"Ginger", "Garlic", "Chili Pepper", "Basil",
 # Other
 "Seaweed", "Konjac" ]


# ───────────────────────────────────────────────
# 原材料抽出関数
# ───────────────────────────────────────────────
def extract_ingredients_from_response(response_text: str) -> list[str]:
    if not response_text:
        return []

    # "原材料:" のセクションを探す
    match_section = re.search(r"原材料:(.*)", response_text, re.IGNORECASE | re.DOTALL)

    if match_section:
        ingredient_text_block = match_section.group(1).strip()
        found_items = re.findall(r"^\s*-\s*(.+)", ingredient_text_block, re.MULTILINE)
        ingredients = [item.strip() for item in found_items]

    return ingredients

async def filter_ingredients_with_ai(
    ai_extracted_ingredients: list[str],
    allowed_ingredients: list[str],
) -> list[str]:
    if not ai_extracted_ingredients:
        return []

    allowed_ingredients_str = ", ".join(allowed_ingredients)
    ai_ingredients_str = "\n".join([f"- {item}" for item in ai_extracted_ingredients])

    prompt = f"""以下の「抽出された原材料リスト」にある各項目について、下記の「許可された原材料リスト」に含まれる項目と実質的に同じものを指しているか判定してください。
    判定の結果、一致すると判断された「許可された原材料リスト」中の項目名だけを、カンマ区切りで一行で出力してください。重複は含めないでください。

    抽出された原材料リスト:
    {ai_ingredients_str}

    許可された原材料リスト:
    [{allowed_ingredients_str}]

    出力例: 豚肉, ピーマン, 玉ねぎ
    """

    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=len(allowed_ingredients) * 10,
        temperature=0.1
    )

    filtered_result_text = response.choices[0].message.content.strip()

    final_ingredients = [
        item.strip() for item in filtered_result_text.split(',')
        if item.strip() and item.strip() in allowed_ingredients
    ]
    return sorted(list(set(final_ingredients)))

@app.post("/analyze-dish", response_model=DishAnalysisResponse)
async def analyze_dish(image: UploadFile = File(...)):
    try:
        # 画像を読み込んでbase64エンコード
        image_data = await image.read()

        # base64エンコード
        encoded = base64.b64encode(image_data).decode("utf-8")
        base64_image = f"data:image/jpeg;base64,{encoded}"

        # Vision APIへのリクエスト
        prompt = """この料理画像を見て、まず料理名を推定してください。
次に、この料理に使われていると思われる主要な原材料をできるだけたくさんリストアップしてください。

応答形式は以下のようにしてください:
料理名: [ここに料理名]
原材料:
- [原材料1]
- [原材料2]
- [原材料3]
..."""

        response = await client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": base64_image},
                        },
                    ],
                }
            ],
            max_tokens=800,
        )

        # レスポンスの解析
        content = response.choices[0].message.content.strip()
        lines = content.split('\n')

        dish_name = lines[0].replace('料理名:', '').strip()

        # 原材料の抽出とフィルタリング
        extracted_ingredients = extract_ingredients_from_response(content)
        filtered_ingredients = await filter_ingredients_with_ai(extracted_ingredients, ingredient_list)

        return DishAnalysisResponse(
            dish_name=dish_name,
            ingredients=filtered_ingredients
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"画像分析エラー: {str(e)}")

@app.post("/explain-ingredients", response_model=list[IngredientInfo])
async def explain_ingredients(ingredient_list: IngredientList):
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": "あなたは料理の専門家です。食材について豊富な知識を持ち食材の育て方や産地なども詳しいです。"
                },
                {
                    "role": "user",
                    "content": f"{ingredient_list.ingredients}上記の食材についてそれぞれの食材ごとに食材が育った環境と食材の豆知識をそれぞれ一文ずつ程度で教えてください。"
                }
            ],
            response_format={"type": "json_object"}
        )

        # レスポンスを解析
        content = response.choices[0].message.content
        try:
            parsed_response = json.loads(content)
            return [IngredientInfo(**item) for item in parsed_response]
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="APIからの応答の解析に失敗しました")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"食材説明の取得に失敗しました: {str(e)}")




