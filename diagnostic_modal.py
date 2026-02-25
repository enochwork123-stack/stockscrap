import modal
import os

app = modal.App("gemini-diagnostic")

@app.function(
    secrets=[modal.Secret.from_name("googlecloud-secret")],
    image=modal.Image.debian_slim().pip_install("google-generativeai")
)
def check_gemini():
    import google.generativeai as genai
    import importlib.metadata
    
    api_key = os.environ.get("GEMINI_API_KEY")
    print(f"Key present: {api_key is not None}")
    if api_key:
        print(f"Key prefix: {api_key[:4]}")
        print(f"Key length: {len(api_key)}")
    
    try:
        version = importlib.metadata.version("google-generativeai")
        print(f"SDK Version: {version}")
    except Exception as e:
        print(f"Could not determine SDK version: {e}")
        
    genai.configure(api_key=api_key)
    
    print("Listing models...")
    try:
        models = [m.name for m in genai.list_models()]
        print(f"All models: {models}")
    except Exception as e:
        print(f"Error listing models: {e}")

@app.local_entrypoint()
def main():
    check_gemini.remote()
