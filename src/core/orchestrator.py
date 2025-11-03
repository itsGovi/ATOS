import ollama
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
import operator

# CONCEPT: LangGraph State
# ANALOGY: Think of this as the "job ticket" that gets passed
#           between workers. It holds all the info about the job.
#           Here, it just holds the list of messages (the chat history).
class AgentState(TypedDict):
    """
    The state for our graph. It's a list of messages.
    'operator.add' means new messages will be ADDED to the list,
    not replace it.
    """
    messages: Annotated[list, operator.add]

# -----------------------------------------------------------------
# TODO - STEP 1: DEFINE YOUR NODE - COMPLETE
# -----------------------------------------------------------------
# A node is just a function that does work.
# This node will be our "worker" that calls the LLM.
def call_model(state: AgentState):
    """Our first, simple node. It just calls the LLM."""
    print("-> Calling model...")
    
    # NOTE: We use the full message list for context, not just the last message.
    # The 'last_message' variable from the original prompt is not strictly needed
    # here but can be useful for logging or debugging.
    
    # 1. Call ollama.chat() with the entire message history from the state
    # This allows the model to maintain conversational context.
    response = ollama.chat(
        model="qwen3-4b:latest",
        messages=state['messages']
    )

    # 2. Get the AI's response content
    ai_content = response['message']['content']
    
    print(f"-> Model response: {ai_content[:50]}...")

    # 3. Create the properly formatted AI message dictionary
    # NOTE: Fixed the 'assitant' typo to 'assistant'.
    ai_message_dict = {
        "role": "assistant",
        "content": ai_content
    }

    # 4. Return a dictionary with the AI's message. 
    # LangGraph will use 'operator.add' to append this to the state['messages'] list.
    return {
        "messages": [ai_message_dict]
    }


# -----------------------------------------------------------------
# TODO - STEP 2: WIRE UP THE GRAPH - COMPLETE
# -----------------------------------------------------------------
# This is where we tell LangGraph the "flowchart"
# -----------------------------------------------------------------

# 1. Define the graph
workflow = StateGraph(AgentState)

# 2. Add the node
# We name the node "model" and link it to the call_model function.
workflow.add_node(
    "model",  
    call_model 
)

# 3. Set the entry point
# All jobs start by going to the "model" node.
workflow.set_entry_point("model") 

# 4. Set the finish point
# After the "model" node is done, the graph finishes.
workflow.add_edge("model", END) 


# 5. Compile the graph
app = workflow.compile()

# -----------------------------------------------------------------
# TODO - STEP 3: RUN THE GRAPH - FINAL TEST
# -----------------------------------------------------------------
if __name__ == "__main__":
    print("Starting ATOS orchestrator (simple)...")
    
    # This is the "input" to our graph
    initial_input = {
        "messages": [
            {
                "role": "user",
                "content": "What is the capital of France?"
            }
        ]
    }

    # First run
    final_state_first_run = None
    for event in app.stream(initial_input):
        print("\n--- Event ---")
        print(event)
        # We need to capture the final state of the graph
        if "__end__" in event:
             # The final state is the value of the last node before END
             final_state_first_run = event["__end__"]
    
    # Let's run it one more time to see it remember context (Task G)
    print("\n\n--- Second Run (Testing Context) ---")
    
    # To maintain context, we take the *final state* of the previous run 
    # (which includes User Q1 + AI A1) and append the new question.
    
    # Create the new follow-up user message
    follow_up_message = {
        "role": "user",
        "content": "What's the weather like there?"
    }

    # The new input is the FINAL state from the previous run, 
    # with the new message ADDED. LangGraph will automatically 
    # use 'operator.add' on the messages list.
    follow_up_input = {
        "messages": [follow_up_message]
    }
    
    # Pass the previous state to the new run
    for event in app.stream(follow_up_input, final_state_first_run):
        print("\n--- Follow-up Event ---")
        print(event)
