import os
import sys
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from backend.agent import compiled_graph

load_dotenv()

def run_cli():
    """
    Standalone CLI loop to interact with the AutoStream agent.
    Maintains local state for the duration of the process.
    """
    print("\n" + "="*50)
    print("Welcome to the AutoStream Agent CLI")
    print("Type 'exit' or 'quit' to end the session.")
    print("="*50 + "\n")
    
    # Initialize fresh state
    state = {
        "messages": [],
        "intent": "unknown",
        "lead_info": {},
        "lead_captured": False,
        "rag_context": ""
    }
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ["exit", "quit"]:
                print("\nGoodbye!\n")
                break
                
            if not user_input:
                continue
            
            # Step 1: Update state with user message
            state["messages"].append(HumanMessage(content=user_input))
            
            # Step 2: Invoke the LangGraph workflow
            result = compiled_graph.invoke(state)
            
            # Update local state variable
            state = result
            
            # Step 3: Print the latest assistant message
            last_message = result["messages"][-1]
            print(f"\nAgent: {last_message.content}")
            
            # Step 4: Print debug info
            print(f"--- [DEBUG] Intent: {result['intent']} | Lead Captured: {result['lead_captured']} ---")
            if result['lead_info'] and any(result['lead_info'].values()):
                print(f"--- [DEBUG] Lead Info: {result['lead_info']} ---\n")
            else:
                print("\n")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}\n")

if __name__ == "__main__":
    run_cli()
