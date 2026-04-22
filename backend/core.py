import os
import time
import logging
from typing import Annotated, Literal, TypedDict, Dict, Any
from pydantic import BaseModel, EmailStr
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool

load_dotenv(override=True)

logger = logging.getLogger(__name__)

class LeadInfo(BaseModel):
    name: str
    email: EmailStr
    platform: str

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    intent: Literal["greeting", "inquiry", "high_intent", "unknown"]
    lead_info: Dict[str, Any]
    lead_captured: bool
    rag_context: str

class LeadInput(BaseModel):
    name: str
    email: EmailStr
    platform: str

@tool("lead_capture", description="Captures user lead information.", args_schema=LeadInput)
def lead_capture_tool(name: str, email: EmailStr, platform: str) -> str:
    print(f"\n[SYSTEM] Lead captured successfully: {name}, {email}, {platform}\n")
    return f"Success: Lead for {name} ({email}) on {platform} has been captured and sent to the sales team."

def get_llm():
    model_name = os.getenv("MODEL", "llama-3.3-70b-versatile")
    return ChatGroq(
        model=model_name,
        temperature=0,
        max_retries=3,
    )

def invoke_with_retry(llm, messages, max_retries=3, base_delay=5):
    """Invoke LLM with exponential backoff retry for transient API errors."""
    for attempt in range(max_retries):
        try:
            return llm.invoke(messages)
        except Exception as e:
            error_str = str(e)
            is_retryable = any(code in error_str for code in ["429", "503", "RESOURCE_EXHAUSTED", "UNAVAILABLE"])
            if is_retryable and attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)  # 5s, 10s, 20s
                logger.warning(f"LLM API error (attempt {attempt + 1}/{max_retries}): retrying in {delay}s...")
                time.sleep(delay)
            else:
                raise

def get_system_prompt():
    system_prompt = os.getenv("SYSTEM_PROMPT", """
    You are an AI assistant representing Autostream. Your goal is to engage with users,     
    understand their needs, and capture lead information accurately.
    
    KEY BEHAVIOR:
    - Capture ALL three fields: Name, Email, and Platform
    - If any field is missing, politely ask the user to provide it
    - Do NOT proceed to lead capture until all fields are collected
    - Be conversational, helpful, and professional
    - Do not use emojis unless the user explicitly uses them
    - Keep responses concise (max 2-3 sentences)
    
    INTENT CATEGORIES (for classification):
    1. Inquiry: General questions about services, pricing, features
    2. Lead: Explicit interest in starting, hiring, or signing up
    3. Support: Help with existing services or technical issues
    4. Other: Anything else
    """)
    return system_prompt

def get_memory_key():
    memory_key = os.getenv("MONGODB_COLLECTION_NAME", "agent_memory")
    return memory_key
