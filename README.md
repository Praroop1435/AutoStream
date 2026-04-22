# AutoStream Agent Project

A professional, LangGraph-powered AI agent platform for AutoStream, featuring a dynamic lead capture system and a real-time dashboard.

## 🚀 Features
- **Llama 3.3 70B Powered**: High-performance reasoning via Groq.
- **Intelligent RAG**: Context-aware responses using a local knowledge base.
- **Stateful Conversations**: Multi-turn memory management using LangGraph.
- **Real-time Lead Dashboard**: Live tracking of captured leads and analytics.
- **Structured Output**: Markdown-formatted responses for better readability.

## 🛠️ Local Setup

Follow these steps to get the project running on your machine.

### 1. Clone and Prepare Environment
```bash
# Clone the repository
git clone https://github.com/Praroop1435/AutoStream.git
cd AutoStream

# Copy environment variables
cp .env.example .env
```
> [!IMPORTANT]
> Open `.env` and add your `GROQ_API_KEY`.

### 2. Backend Setup
We use `uv` for lightning-fast dependency management.
```bash
# Install dependencies
uv sync

# Run the FastAPI server
uv run uvicorn backend.main:app --reload
```
The backend will be available at `http://localhost:8000`.

### 3. Frontend Setup
In a new terminal window:
```bash
cd frontend

# Install dependencies
npm install

# Start the Next.js development server
npm run dev
```
The dashboard will be available at `http://localhost:3000`.

## 🧠 Architecture Explanation

### Why LangGraph over AutoGen?
We specifically chose **LangGraph** over frameworks like AutoGen because building a reliable sales and support agent requires fine-grained, deterministic control over the conversational flow. While AutoGen excels at autonomous multi-agent brainstorming, the AutoStream assistant needs strict, predictable boundaries: classifying intents, retrieving specific context (RAG), and reliably capturing leads without hallucinating tool calls. 

LangGraph’s **StateGraph** architecture allows us to define explicit nodes and conditional routing. For instance, the agent is structurally guided through a deterministic pipeline that guarantees a lead capture form is generated if and only if high intent is detected.

### How State is Managed
State is maintained via a strongly typed `AgentState` dictionary. We use LangGraph’s `Annotated[list, add_messages]` to seamlessly handle conversation history. As a user interacts with the FastAPI backend, their `session_id` and `user_id` are mapped to our local SQLite database. On each incoming request, we load their historical messages from the database directly into the `AgentState`. As the graph executes, individual nodes read from the state (e.g., checking for missing lead fields) and append new AIMessages or tool outcomes. Finally, the generated messages are synced back to the database, providing a robust, long-term memory that survives server restarts and scales efficiently.

## 📱 WhatsApp Deployment Question

**How would you integrate this agent with WhatsApp using Webhooks?**

Integrating the AutoStream agent with WhatsApp involves establishing a two-way communication channel using the Meta WhatsApp Cloud API:

1. **Webhook Endpoint Setup**: We expose a `POST /webhook` route on our FastAPI server to act as the listener for Meta's incoming events. We also need a `GET /webhook` route to handle Meta's initial token verification challenge.
2. **Meta Dashboard Configuration**: In the Meta Developer Portal, we configure the webhook URL (making it publicly accessible via a cloud deployment or ngrok) and subscribe to `messages` webhooks.
3. **Handling Incoming Messages**: When a user sends a message, Meta sends a JSON payload to our webhook. We extract the sender's phone number (`wa_id`) and the message body.
4. **Session Mapping**: We use the `wa_id` as the unique `session_id` to fetch the user's historical `AgentState` from our database.
5. **Agent Execution**: We invoke our LangGraph pipeline with the new message and the retrieved state.
6. **Sending Replies**: Once the agent generates a response, we make a `POST` request back to the WhatsApp Cloud API's `/messages` endpoint—authenticated with our Page Access Token—to deliver the response directly to the user's WhatsApp interface.
