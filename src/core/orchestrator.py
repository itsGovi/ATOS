import ollama
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
import operator

# --- AGENT STATE DEFINITION ---
class AgentState(TypedDict):
    """The extended state for our orchestrator."""
    messages: Annotated[list, operator.add]
    summary_context: str
    step_count: Annotated[int, operator.add]
    chat_id: str

# -----------------------------------------------------------------
# TODO - STEP 1A: DEFINE THE ROUTER NODE (The Conditional Edge)
# -----------------------------------------------------------------
def route_to_summary(state: AgentState) -> str:
    """
    Decides whether to summarize or call the main model based on step_count.
    Must return one of: "summarize", "call_model", or END.
    """
    # NOTE: The check should be for steps >= 5 to trigger *after* the 5th user turn.
    # The check for divisibility by 5 uses the modulo operator: % 5 == 0
    if state['step_count'] % 5 == 0 and state['step_count'] > 0:
        return "summarize"
    else:
        return "call_model"


# -----------------------------------------------------------------
# TODO - STEP 1B: DEFINE THE SUMMARIZATION NODE (The 4B Worker)
# -----------------------------------------------------------------
def summarize_conversation(state: AgentState) -> dict:
    """
    Generates a condensed summary of the current conversation history.
    This node also handles the step_count reset for the next cycle.
    """
    print("-> Summarizer: Generating new summary...")

    # TODO: Define the prompt for the summarizer model. 
    # HINT: Use the full raw messages list (state['messages']). The prompt 
    # should instruct the LLM to provide a brief, actionable summary for context.
    summarization_prompt = [
        {"role": "system", "content": "You are a concise summarization expert. Condense the following chat history into a single, short paragraph that retains all key facts and instructions."},
        # TODO: Add the full message history here to be summarized
        *state['messages'] 
    ]
    
    # TODO: Call Ollama with the summarization prompt
    summary_response = ollama.chat(
        model="qwen3-4b:latest", 
        messages=summarization_prompt
    )
    
    # TODO: Extract the new summary content
    new_summary = summary_response['message']['content']
    
    # Calculate the reset value: Subtract the current count to set it back to 0.
    reset_count = -state['step_count']
    
    print(f"-> Summarizer: New Summary '{new_summary[:30]}...' | Resetting counter by {reset_count}")
    
    # The node updates the summary and resets the counter for the next 5-turn cycle.
    return {
        "summary_context": new_summary,
        "step_count": reset_count # operator.add makes 5 + (-5) = 0
    }


# -----------------------------------------------------------------
# TODO - STEP 1C: UPDATE THE CALL_MODEL NODE (The 7B Worker)
# -----------------------------------------------------------------
def call_model(state: AgentState):
    """
    The main model node. It reads the summary_context and the latest message.
    """
    print("-> Calling model...")
    
    # TODO: Build the optimal list of messages to send to the 7B model for efficiency.
    # HINT: Only send the summary and the *latest* user message, 
    # NOT the full raw history, to save VRAM and latency.
    llm_input_messages = []

    # 1. Add the condensed summary as the top-level context (if it exists)
    if state.get("summary_context"):
        llm_input_messages.append({
            "role": "system",
            "content": f"PREVIOUS CONTEXT: {state['summary_context']}\n---\n"
        })
        # 2. Add ONLY the last raw user message for the current query
        llm_input_messages.append(state['messages'][-1])
    else:
        # If no summary exists (first 5 turns), use the full history for context
        llm_input_messages.extend(state['messages'])

    response = ollama.chat(
        model="qwen3-4b:latest",
        messages=llm_input_messages
    )

    ai_content = response['message']['content']
    print(f"-> Model response: {ai_content[:50]}...")

    ai_message_dict = {
        "role": "assistant",
        "content": ai_content
    }

    # The node returns the message and the step increment.
    return {
        "messages": [ai_message_dict],
        "step_count": 1 # Increment the counter after the AI replies
    }


# -----------------------------------------------------------------
# STEP 2: WIRE UP THE GRAPH (The Flowchart Manager)
# -----------------------------------------------------------------
workflow = StateGraph(AgentState)

# Add the three required nodes
workflow.add_node("router", route_to_summary) 
workflow.add_node("summarize", summarize_conversation)
workflow.add_node("call_model", call_model)

# Set the entry point to the router
workflow.set_entry_point("router")

# Set the conditional edge from the router
workflow.add_conditional_edges(
    "router",          
    route_to_summary,  
    {
        "summarize": "summarize", # If router returns "summarize", go here
        "call_model": "call_model", # If router returns "call_model", go here
    }
)

# Set the edges from the worker nodes back to the END
# CRITICAL: After summarization, we must still go to the model to answer the user!
workflow.add_edge("summarize", "call_model") 
workflow.add_edge("call_model", END) 


# Compile the graph
app = workflow.compile()

# -----------------------------------------------------------------
# STEP 3: RUN THE GRAPH (Test the Conditional Logic)
# -----------------------------------------------------------------

if __name__ == "__main__":
    print("Starting ATOS orchestrator (conditional)...")
    
    # Run 1: Start Conversation (Step 1)
    # The router should send this to "call_model"
    initial_input = {
        "messages": [
            {
                "role": "user",
                "content": "Turn 1: What is the capital of France?"
            }
        ],
        "summary_context": "The chat has just started.",
        "step_count": 1, 
        "chat_id": "initial-context-test-001" 
    }

    print("\n--- RUN 1 (Step 1 -> call_model) ---")
    final_state = initial_input
    for event in app.stream(initial_input):
        if event.get("call_model"):
            print(f"-> Model Node Ran. Next: {event.get('call_model')}")
        if "__end__" in event:
             final_state = event["__end__"]
    
    
    # Run 4 more times to hit step_count = 5 (the summarization trigger)
    # We will simulate the next 4 user turns by passing the state forward.
    for i in range(2, 6): # This loop simulates Turns 2, 3, 4, 5
        print(f"\n--- RUN {i} (Step {final_state['step_count'] + 1}) ---")
        
        # New input: only the new message and the step increment
        new_input = {
            "messages": [
                {"role": "user", "content": f"Turn {i}: Another question to build up history."}
            ],
            "step_count": 1 
        }
        
        current_state = final_state
        final_state = None
        
        # Check if we should hit summarization on this turn (i.e., if current_state['step_count'] + 1 == 5)
        # Note: The router *receives* the state, including the new 'step_count': 1 from new_input 
        # that LangGraph adds to the existing count.
        
        # Run the graph
        for event in app.stream(new_input, current_state):
             if event.get("summarize"):
                 print("✅ ROUTER HIT SUMMARIZE NODE!")
             elif event.get("call_model"):
                 print("-> Router Hit Call Model Node")
             
             if "__end__" in event:
                 final_state = event["__end__"]

    print(f"\n--- END OF SIMULATION ---")
    print(f"✅ FINAL STEP COUNT: {final_state['step_count']} (Expected 1 or 5, depending on the last action)")
    print(f"✅ FINAL SUMMARY: {final_state['summary_context']}")