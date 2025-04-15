# backend/app.py
from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import openai                     # openai>=1.0.0

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
    allow_origins=["http://localhost:3000"],  # フロントの URL
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

# ───────────────────────────────────────────────
# /chat エンドポイント
# ───────────────────────────────────────────────
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": req.message},
            ],
            temperature=0.7,
            max_tokens=256,
        )
        reply_text = response.choices[0].message.content.strip()
        return ChatResponse(reply=reply_text)

    except openai.OpenAIError as e:
        # OpenAI 側のエラーをラップして返却
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {e.user_message}") from e
