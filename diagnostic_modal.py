import os
import modal

app = modal.App("diagnostic-gemini-v2")

image = (
    modal.Image.debian_slim()
    .pip_install("google-generativeai")
)

@app.function(
    image=image,
    secrets=[modal.Secret.from_name("googlecloud-secret")]
)
def check_gemini():
    import google.generativeai as genai
    
    api_key = os.environ.get("GEMINI_API_KEY")
    print(f"Key present: {bool(api_key)}")
    if not api_key:
        return

    genai.configure(api_key=api_key)
    
    print("Listing models and their supported methods...")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"Model: {m.name} | Methods: {m.supported_generation_methods}")
    except Exception as e:
        print(f"Failed to list models: {e}")

    # Trial with explicit v1 if possible (SDK usually handles this, but let's check)
    print("\nAttempting a minimal 'Hello' call with gemini-2.0-flash...")
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content("Hello")
        print(f"Success! Response: {response.text}")
    except Exception as e:
        print(f"Model gemini-2.0-flash failed: {e}")

@app.local_entrypoint()
def main():
    check_gemini.remote()
