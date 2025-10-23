# Create this file at: src/core/orchestrator.py

import ollama
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
import operator

# CONCEPT: LangGraph State
# ANALOGY: Think of this as the "job ticket" that gets passed
#          between workers. It holds all the info about the job.
#          Here, it just holds the list of messages (the chat history).
class AgentState(TypedDict):
    """
    The state for our graph. It's a list of messages.
    'operator.add' means new messages will be ADDED to the list,
    not replace it.
    """
    messages: Annotated[list, operator.add]

# -----------------------------------------------------------------
# TODO - STEP 1: DEFINE YOUR NODE
# -----------------------------------------------------------------
# A node is just a function that does work.
# This node will be our "worker" that calls the LLM.
# 
# Your task: Complete this function.
# It should:
# 1. Get the user's *last* message from the 'state' dictionary.
# 2. Call 'ollama.chat()' with that message.
# 3. Return a new 'state' dictionary with the AI's response added.
# -----------------------------------------------------------------
def call_model(state: AgentState):
    """Our first, simple node. It just calls the LLM."""
    print("-> Calling model...")
    
    # Get the last message from the state
    last_message = state['messages'][-1]

    # TODO: Call ollama.chat()
    # HINT: The 'ollama.chat' function takes a 'model' string
    #       and a 'messages' list.
    #       Use "qwen3-4b:latest" for the model.
    #       The 'messages' list should be the 'state['messages']'
    
    response = ollama.chat(
        model= # TODO: "Your model name"
        messages= # TODO: The full message list from the state
    )

    # TODO: Get the AI's response content from the 'response' object
    # HINT: The response is a dictionary. You want the message content.
    #       print(response) to see its structure!
    ai_message = response['message']['content']
    
    print(f"-> Model response: {ai_message[:50]}...")

    # TODO: Return a dictionary with the AI's message
    # HINT: It should be in the format {'messages': [ai_message]}
    #       LangGraph will use 'operator.add' to add it to the state.
    return {
        "messages": [ai_message]
    }


# -----------------------------------------------------------------
# TODO - STEP 2: WIRE UP THE GRAPH
# -----------------------------------------------------------------
# This is where we tell LangGraph the "flowchart"
# -----------------------------------------------------------------

# 1. Define the graph
workflow = StateGraph(AgentState)

# 2. Add the node
#    This tells the graph: "You have a worker named 'model'"
#    "When you call 'model', it should run the 'call_model' function"
workflow.add_node(
    "model",  # TODO: Give your node a name (e.g., "model")
    call_model  # TODO: Tell it which function to run
)

# 3. Set the entry point
#    This tells the graph: "When a job starts, send it to 'model' first."
workflow.set_entry_point("model") # TODO: Put your node's name here

# 4. Set the finish point
#    This tells the graph: "After the 'model' node is done,
#    the whole job is 'END'ed."
workflow.add_edge("model", END) # TODO: Put your node's name here


# 5. Compile the graph
#    This turns our flowchart into a runnable "app"
app = workflow.compile()

# -----------------------------------------------------------------
# TODO - STEP 3: RUN THE GRAPH
# -----------------------------------------------------------------

# This is how you run your new "app"
# We'll put it in a 'main' block to be professional
if __name__ == "__main__":
    print("Starting ATOS orchestrator (simple)...")
    
    # This is the "input" to our graph
    # HINT: It needs to match the 'AgentState' format!
    initial_input = {
        "messages": [
            {
                "role": "user",
                "content": "What is the capital of France?"
            }
        ]
    }

    # 'stream()' runs the graph and gives us the final state
    for event in app.stream(initial_input):
        # 'event' will have the data from each node as it runs
        print("\n--- Event ---")
        print(event)

    # Let's run it one more time to see it remember context
    print("\n\n--- Second Run (Testing Context) ---")
    
    # TODO: How would you ask a follow-up question?
    # HINT: You need to pass *all* the messages from the *last* run,
    #       plus your new question.
    #       But for today, just running it once is enough.
    #       Let's just prove it works.
    
    # For now, let's just ask a new question
    follow_up_input = {
        "messages": [
            {
                "role": "user",
                "content": "What's the weather like there?"
            }
        ]
    }
    
    for event in app.stream(follow_up_input):
        print("\n--- Follow-up Event ---")
        print(event)