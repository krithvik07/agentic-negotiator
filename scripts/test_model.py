from gpt4all import GPT4All

# Dynamically select an available model (avoid hardcoding names that might 404)
models = GPT4All.list_models()
if not models:
    raise RuntimeError("No GPT4All models available from the registry. Check your internet connection.")

# Prefer smaller quantized gguf models (q4 or q4_0)
preferred = None
for m in models:
    fname = m.get("filename", "").lower()
    if ".gguf" in fname and ("q4_0" in fname or "q4" in fname):
        preferred = m["filename"]
        break

# Fallback: any gguf model
if preferred is None:
    for m in models:
        fname = m.get("filename", "").lower()
        if ".gguf" in fname:
            preferred = m["filename"]
            break

# Final fallback: first model in registry
model_name = preferred or models[0]["filename"]
print(f"Using GPT4All model: {model_name}")

model = GPT4All(model_name)

prompt = "Say hello in a friendly way."

with model.chat_session():
    response = model.generate(prompt, max_tokens=128)

print("Response:", response)
