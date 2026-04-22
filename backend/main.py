import os
from typing import Dict, List, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from backend.agent import compiled_graph
from backend.auth.router import router as auth_router
from backend.auth.utils import verify_token
from backend.db.database import init_db, load_messages, save_messages
from dotenv import load_dotenv

load_dotenv(override=True)

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    intent: str
    lead_captured: bool

class WebhookPayload(BaseModel):
    object: str
    entry: List[Dict[str, Any]]

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

async def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload["user_id"]

def get_initial_state(messages: list, user_id: int) -> dict:
    return {
        "messages": messages,
        "user_id": user_id,
        "intent": "unknown",
        "lead_info": {},
        "lead_captured": False,
        "rag_context": ""
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, user_id: int = Depends(get_current_user)):
    session_id = request.session_id
    
    db_messages = await load_messages(user_id, session_id)
    current_state = get_initial_state(db_messages, user_id)
    
    user_msg = HumanMessage(content=request.message)
    current_state["messages"].append(user_msg)
    
    try:
        result = compiled_graph.invoke(current_state)
        
        await save_messages(user_id, session_id, result["messages"])
        
        assistant_reply = result["messages"][-1].content
        
        return ChatResponse(
            session_id=session_id,
            reply=assistant_reply,
            intent=result.get("intent", "unknown"),
            lead_captured=result.get("lead_captured", False)
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook")
async def whatsapp_webhook(payload: WebhookPayload):
    print(f"Received Webhook Payload: {payload.model_dump()}")
    return {"status": "received"}

@app.get("/leads")
async def fetch_leads(user_id: int = Depends(get_current_user)):
    from backend.db.database import get_leads
    leads = await get_leads(user_id)
    return {"leads": leads}

@app.get("/")
async def root():
    model = os.getenv("MODEL", "llama-3.3-70b-versatile")
    return {
        "status": "ok",
        "service": "AutoStream Agent API",
        "model": model
    }
