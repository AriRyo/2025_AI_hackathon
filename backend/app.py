# backend/app.py
from fastapi import FastAPI
from routes import chat

app = FastAPI(title="Chat Backend", description="Backend API for Chat App", version="0.1.0")

app.include_router(chat.router, prefix="/chat")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
