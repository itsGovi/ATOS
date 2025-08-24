import ollama

def call_orchestrator(prompt):
    model_response = ollama.chat(model='qwen3-4b', messages=[
        {
            'role': 'user',
            'content': prompt
        }
    ])
    return model_response

prompt = 'hi, how are ya!'
output = call_orchestrator(prompt)
if __name__ == '__main__':
    call_orchestrator(prompt)
    print(output)