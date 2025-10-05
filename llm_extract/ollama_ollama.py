import ollama

def ollama_ollama_call(prompt: str, model_name: str, model_options: dict) -> dict:
    response = ollama.generate(
        model=model_name,
        prompt=prompt,
        options=model_options,
        stream=False
    )
    meta = {k: v for k, v in vars(response).items() if k not in ['response', 'context']}
    response_dict = {
        'data': {
            'text': response.response,
        },
        'meta': meta,
    }
    return response_dict

# Test ollama server up and running:
# curl http://localhost:11434/api/generate -d '{
#   "model": "gemma3",
#   "prompt": "Why is the sky blue?",
#   "stream": false
# }'