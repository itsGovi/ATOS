import ollama

model_name = "qwen2.5-coder-7b:latest"

user_input = input("Ask the model: ")

response = ollama.generate(
    model= model_name,
    prompt= user_input
)

print("-"*18)
print(f"Model {model_name}:")
print(response['response'])