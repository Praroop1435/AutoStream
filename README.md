# AutoStream Agent Project

A complete LangGraph-based AI agent for AutoStream, a fictional SaaS company providing automated video editing tools.

## Setup Instructions

1. **Prerequisites**: Ensure you have Python 3.11+ and `uv` installed.
2. **Environment**:
   - Copy `.env.example` to `.env`.
   - Add your `ANTHROPIC_API_KEY` (and others if needed).
3. **Install Dependencies**:
   ```bash
   uv add langchain-core langchain-anthropic langchain-openai langchain-google-genai langgraph fastapi "uvicorn[standard]" "pydantic[email]" python-dotenv httpx
   uv sync
   ```

## Running the Project

### CLI Mode (Direct Interaction)
```bash
python main.py
```

### API Mode (FastAPI Server)
```bash
uvicorn api.main:app --reload
```

## Architecture Explanation

### Why LangGraph?
LangGraph was chosen over frameworks like AutoGen because it provides fine-grained control over the agent's logic through a **StateGraph**. This allowed us to explicitly define transitions between intent classification, knowledge retrieval (RAG), and tool execution. LangGraph's cyclic capability is perfect for the conversational flow where the agent might need to loop back to ask for missing lead information.

### State Management
Memory is managed via `AgentState` (a `TypedDict`), which uses LangGraph's `Annotated[list, add_messages]` for automatic thread-safe message merging. This ensures the conversation history is preserved across turns without manual concatenation, maintaining the context for 5-6+ turns as required.

### Tool Calling Discipline
The conditional routing in `agent/graph.py` ensures that the `lead_capture` tool is **never** triggered prematurely. The graph only routes to the `execute_lead_capture` node after the `generate_response` node confirms that all three required fields (`name`, `email`, `platform`) have been collected and that the lead hasn't been captured yet.

## WhatsApp Deployment

1. **Webhook Exposure**: Expose the `POST /webhook` endpoint using a public URL (e.g., via `ngrok` or a cloud provider).
2. **Meta Dashboard**: Register the URL in the Meta WhatsApp Business API dashboard under Webhooks.
3. **Session Processing**:
   - Parse the incoming `wa_id` (sender's phone number) from the WhatsApp payload.
   - Use `wa_id` as the `session_id` in our `api/routes.py` to isolate state across users.
4. **Sending Replies**: Use the WhatsApp Cloud API's `messages` endpoint to send the agent's response back to the user's phone number.
