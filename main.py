import asyncio
import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import rag_service

app = FastAPI()

@app.get("/")
def home():
    return {"message": "WebSocket RAG Backend is Running"}

@app.websocket("/ws/rag")
async def websocket_rag(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            query = await websocket.receive_text()
            print(f"收到查询: {query}")
            
            async for chunk in rag_service.generate_response(query):
                await websocket.send_text(chunk)
            
            await websocket.send_text("[DONE]")
            
    except WebSocketDisconnect:
        print("WebSocket 连接断开")

