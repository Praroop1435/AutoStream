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

## 🧠 Architecture

### Why LangGraph?
LangGraph provides fine-grained control over the agent's logic through a **StateGraph**. This allows us to explicitly define transitions between intent classification, knowledge retrieval (RAG), and tool execution.

### Persistence & Leads
Captured leads are stored in a local SQLite database (`autostream.db`). The dashboard fetches these in real-time, allowing you to track user interest and platforms (YouTube, TikTok, etc.) dynamically.

### AI Model
We use **Meta's Llama 3.3 70B** via the **Groq** API for ultra-low latency and high-quality responses, configured with exponential backoff retries to handle API demand spikes.
