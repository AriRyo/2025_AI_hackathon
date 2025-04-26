# backend/app.py
from __future__ import annotations

import os
import base64
import mimetypes
from io import BytesIO
from pathlib import Path
import json

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
            model="gpt-4o",
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
        ingredients = []
        
        for line in lines[1:]:
            if line.strip().startswith('-'):
                ingredient = line.strip('- ').strip()
                ingredients.append(ingredient)

        return DishAnalysisResponse(
            dish_name=dish_name,
            ingredients=ingredients
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




