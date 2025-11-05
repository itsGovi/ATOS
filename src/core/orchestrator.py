import ollama
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
import operator

class AgentState(TypedDict):
    """
    The extended state for our graph, supporting context management (summary)
    and conversational flow (step count).
    """
    # 1. RAW CHAT HISTORY (Policy: Append)
    messages: Annotated[list, operator.add]
    
    # 2. CONDENSED HISTORY (Policy: Replace)
    # This stores the output of the summarizer model.
    summary_context: str
    
    # 3. CONVERSATION COUNTER (Policy: Increment)
    # Tracks the number of user/agent turns for summarization trigger.
    step_count: Annotated[int, operator.add]
    
    # 4. CHAT IDENTIFIER (Policy: Replace)
    # Used for naming the chat file/log.
    chat_id: str

# -----------------------------------------------------------------
# TODO - STEP 1A: DEFINE THE ROUTER NODE (The Quality Control Gate)
# -----------------------------------------------------------------
# This node will check the step_count and decide the next path.
def route_to_summary(state: AgentState) -> str:
    """
    Decides whether to summarize or call the main model based on step_count.
    Must return the name of the NEXT node (a string).
    """
    print(f"-> Router: Current Step Count: {state['step_count']}")
    
    # TODO: Implement the conditional logic for summarization.
    # If the step_count is the 5th step, route to the summarizer.
    # Otherwise, route to the main model node.
    if state["step_count"] % 5 == 0: # Replace False with your count logic
        create_summary = 
        step_count = 0
    else:
        return call_model


# -----------------------------------------------------------------
# TODO - STEP 1B: DEFINE THE SUMMARIZATION NODE (The 4B Worker)
# -----------------------------------------------------------------
# This node uses the raw messages to generate a short context summary.
def summarize_conversation(state: AgentState) -> dict:
    """
    Generates a condensed summary of the current conversation history.
    """
    print("-> Summarizer: Generating new summary...")

    # TODO: Formulate a prompt for the 4B model to summarize the history.
    # The 'messages' list is available in the state.
    
    # HINT: You will need to make an ollama.chat() call here, using a smaller model 
    # and the full 'messages' list.
    
    # TODO: Call Ollama with the summarization prompt
    summary_response = ollama.chat(
        model="qwen3-4b:latest", # Use the fast, local model
        messages=state['messages'] # Pass the full history for summarization
    )
    
    # TODO: Extract the new summary content
    new_summary = "A Placeholder Summary."
    
    # NOTE: The summarizer only updates the 'summary_context'. 
    # It does NOT add a message to the raw 'messages' list.
    return {
        "summary_context": new_summary,
        # IMPORTANT: The summarization itself counts as a step in the process.
        "step_count": 1 # Use operator.add to increment the count
    }


# -----------------------------------------------------------------
# TODO - STEP 1C: UPDATE THE CALL_MODEL NODE (The 7B Worker)
# -----------------------------------------------------------------
# This node now needs to USE the 'summary_context' for efficiency.
def call_model(state: AgentState):
    """
    Our main model node. It reads the summary_context and the latest message.
    """
    print("-> Calling model...")
    
    # TODO: Build the final list of messages to send to the 7B model.
    # HINT: The list should contain:
    # 1. A SYSTEM message using the 'summary_context'.
    # 2. The most recent user message (the last message in the 'messages' list).
    
    # For now, we will use the full history as a placeholder
    llm_input_messages = state['messages']

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

    # The node MUST return the message and the step increment.
    return {
        "messages": [ai_message_dict],
        "step_count": 1 # Increment the counter after the AI replies
    }


# -----------------------------------------------------------------
# TODO - STEP 2: WIRE UP THE GRAPH (The Flowchart Manager)
# -----------------------------------------------------------------
# The new flow: ENTRY -> router -> (summarize | call_model) -> END
# -----------------------------------------------------------------

# 1. Define the graph
workflow = StateGraph(AgentState)

# 2. Add the nodes
# TODO: Add the three required nodes to the workflow object.
workflow.add_node("router", route_to_summary) 
workflow.add_node("summarize", summarize_conversation)
workflow.add_node("call_model", call_model)

# 3. Set the entry point (It must be the router!)
workflow.set_entry_point("router")

# 4. Set the conditional edge from the router
# The router must define the path based on its string output.
# The keys here MUST match the strings returned by route_to_summary()
workflow.add_conditional_edges(
    "router",          # Start node name
    route_to_summary,  # The function to run (LangGraph can optionally run it here too)
    {
        # Map the output string to the next node name
        "summarize": "summarize", 
        "call_model": "call_model",
        END: END # If you want the router to sometimes end the graph
    }
)

# 5. Set the edges from the worker nodes back to the END
# TODO: Add an edge from 'summarize' to 'call_model' so it answers the user after summarization.
workflow.add_edge("summarize", "call_model") 
workflow.add_edge("call_model", END) 


# 6. Compile the graph
app = workflow.compile()

# -----------------------------------------------------------------
# TODO - STEP 3: RUN THE GRAPH (Test the Counter and Router)
# -----------------------------------------------------------------

if __name__ == "__main__":
    print("Starting ATOS orchestrator (conditional)...")
    
    # INITIAL INPUT: Must include the new state keys
    initial_input = {
        "messages": [
            {
                "role": "user",
                "content": "Start conversation. What is the capital of France?"
            }
        ],
        # TODO: Provide starting values for the new state keys
        "summary_context": "",
        "step_count": 1, 
        "chat_id": "initial-context-test-001" 
    }

    print("\n--- Running 1st Conversation Turn (Should skip summarization) ---")
    final_state_run_1 = None
    for event in app.stream(initial_input):
        print(event)
        if "__end__" in event:
             final_state_run_1 = event["__end__"]
    print(f"\nFINAL STATE: Step Count = {final_state_run_1['step_count']}")
    
    # TODO: Run the graph 4 more times (by passing the final state and new input)
    # to hit the 'summarize' condition on the 5th run. 
    # Remember to capture the final state of each run to pass to the next!