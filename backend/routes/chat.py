# backend/routes/chat.py
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import openai
from dotenv import load_dotenv

# .env の環境変数をロード
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest):
    try:
        response = openai.Chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": chat_request.message},
            ],
        )
        reply_text = response.choices[0].message.content.strip()
        return ChatResponse(reply=reply_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
