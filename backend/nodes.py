import json
import os
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from backend.core import AgentState, LeadInfo, lead_capture_tool, get_llm, invoke_with_retry

def classify_intent(state: AgentState) -> AgentState:
    llm = get_llm()
    last_message = state["messages"][-1].content
    
    system_prompt = (
        "You are an intent classifier for AutoStream, a SaaS for automated video editing.\n"
        "Classify the user's message into exactly one of these categories: 'greeting', 'inquiry', 'high_intent', 'unknown'.\n"
        "Categories:\n"
        "- 'greeting': Just saying hello or hi.\n"
        "- 'inquiry': Asking about pricing, features, or policies.\n"
        "- 'high_intent': Expressing strong desire to sign up, buy, or try a specific plan.\n"
        "- 'unknown': Anything else.\n"
        "Output ONLY the category name."
    )
    
    response = invoke_with_retry(llm, [SystemMessage(content=system_prompt), HumanMessage(content=last_message)])
    intent = response.content.strip().lower()
    
    if intent not in ["greeting", "inquiry", "high_intent", "unknown"]:
        intent = "unknown"
        
    return {**state, "intent": intent}

def retrieve_context(state: AgentState) -> AgentState:
    kb_path = os.path.join(os.path.dirname(__file__), "..", "knowledge_base", "autostream_kb.json")
    try:
        with open(kb_path, "r") as f:
            kb = json.load(f)
    except FileNotFoundError:
        return {**state, "rag_context": ""}

    last_message = state["messages"][-1].content.lower()
    matched_info = []

    for plan in kb.get("plans", []):
        if plan["name"].lower() in last_message or any(f.lower() in last_message for f in plan["features"]):
            features_str = ", ".join(plan["features"])
            matched_info.append(f"{plan['name']} Plan: {plan['price']} — {features_str}.")

    for policy in kb.get("policies", []):
        if any(word in last_message for word in ["refund", "support", "cancel", "policy"]):
            matched_info.append(policy)

    rag_context = "\n".join(matched_info) if matched_info else ""
    return {**state, "rag_context": rag_context}

def generate_response(state: AgentState) -> AgentState:
    llm = get_llm()
    rag_snippet = f"\nRelevant Information: {state['rag_context']}" if state["rag_context"] else ""
    
    system_prompt = (
        "You are a friendly and helpful sales assistant for AutoStream. "
        "AutoStream provides automated video editing tools for creators.\n"
        "Your goal is to answer questions accurately and guide high-intent users to sign up.\n"
        "FORMATTING: Use Markdown to structure your response professionally. "
        "Use ### headers for main sections, --- horizontal rules for logical breaks, "
        "and bold keywords for emphasis. Ensure proper vertical spacing between sections. "
        "Always end with a '---' followed by a '### Next Steps' section if applicable.\n"
        f"{rag_snippet}\n\n"
        "LEAD CAPTURE LOGIC:\n"
        "If the user's intent is 'high_intent', you must collect their Name, Email, and Creator Platform.\n"
    )
    
    lead_info = state.get("lead_info", {})
    if state["intent"] == "high_intent":
        missing_fields = []
        if not lead_info.get("name"): missing_fields.append("Name")
        if not lead_info.get("email"): missing_fields.append("Email")
        if not lead_info.get("platform"): missing_fields.append("Creator Platform")
        
        if missing_fields:
            system_prompt += (
                f"\nYou are currently missing the following information: {', '.join(missing_fields)}. "
                "Ask the user to provide ALL of the missing information at once in your response. "
                "Present a clean Markdown bulleted list or a 'form' format so they can easily fill it out in one go. "
                "Do NOT ask for them one by one."
            )
        else:
            system_prompt += "\nYou have all lead info. Confirm that you are processing their sign-up and provide exciting details about their next steps."

    response = invoke_with_retry(llm, [SystemMessage(content=system_prompt)] + state["messages"])
    last_user_message = state["messages"][-1].content
    extraction_prompt = (
        "Extract lead information (name, email, platform) from the text below.\n"
        "Return as a JSON object. Use null if a field is not found.\n"
        f"Text: {last_user_message}"
    )
    
    extracted = invoke_with_retry(llm, [SystemMessage(content=extraction_prompt)])
    try:
        data = json.loads(extracted.content)
        for key in ["name", "email", "platform"]:
            if data.get(key) and not lead_info.get(key):
                lead_info[key] = data[key]
    except:
        pass

    return {
        **state, 
        "messages": [AIMessage(content=response.content)],
        "lead_info": lead_info
    }

def execute_lead_capture(state: AgentState) -> AgentState:
    lead_info = state.get("lead_info", {})
    user_id = state.get("user_id")
    try:
        validated_lead = LeadInfo(**lead_info)
        result = lead_capture_tool.invoke({
            "name": validated_lead.name,
            "email": validated_lead.email,
            "platform": validated_lead.platform
        })
        
        # Save to DB asynchronously
        import asyncio
        from backend.db.database import save_lead
        # We are in a synchronous LangGraph node, but we can run async code
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(save_lead(user_id, validated_lead.name, validated_lead.email, validated_lead.platform))
        else:
            asyncio.run(save_lead(user_id, validated_lead.name, validated_lead.email, validated_lead.platform))

        return {
            **state,
            "lead_captured": True,
            "messages": [AIMessage(content=f"System Notification: {result}")]
        }
    except Exception as e:
        return {
            **state,
            "messages": [AIMessage(content=f"Error capturing lead: {str(e)}")]
        }
