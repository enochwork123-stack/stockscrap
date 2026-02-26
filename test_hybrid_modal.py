import modal
import os
import json

app = modal.App("test-hybrid-direct")

image = (
    modal.Image.debian_slim()
    .pip_install("google-generativeai")
)

def generate_ai_analysis_logic(ticker, news_context, price_context=""):
    """
    Hybrid Intelligence Engine logic for testing.
    """
    if ticker == "GOOG":
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            print(f"DEBUG: Found Gemini API key for {ticker}. Attempting Gemini call...")
            
            # Try a few models in order of preference
            models_to_try = [
                'gemini-2.0-flash',
                'gemini-1.5-flash-latest',
                'gemini-1.5-pro-latest',
                'gemini-pro'
            ]
            
            for model_name in models_to_try:
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=api_key)
                    print(f"DEBUG: Attempting Gemini call with model: {model_name}")
                    model = genai.GenerativeModel(model_name)
                    
                    prompt = f"""
                    You are a senior financial analyst. Based on the news headlines provided below for {ticker}, 
                    please provide a 100-200 word sentimental analysis summary. 
                    Focus on the themes, investor sentiment, and potential market impact.
                    
                    Keep the TECHNICAL_OUTLOOK concise (2-3 sentences).
                    
                    NEWS HEADLINES:
                    {news_context}
                    
                    PRICE CONTEXT:
                    {price_context}
                    
                    Format the response as JSON:
                    {{
                        "summary": "...",
                        "technical_outlook": "..."
                    }}
                    """
                    
                    response = model.generate_content(
                        prompt,
                        generation_config=genai.GenerationConfig(
                            response_mime_type="application/json",
                        ),
                    )
                    
                    data = json.loads(response.text)
                    print(f"DEBUG: Successfully received Gemini response for {ticker} using {model_name}")
                    return {
                        "summary": data.get("summary", ""),
                        "technical_outlook": data.get("technical_outlook", ""),
                        "model_used": f"Gemini-{model_name} (Advanced)"
                    }
                except Exception as e:
                    print(f"DEBUG: Gemini failed for {ticker} with {model_name}. Error: {str(e)}")
                    # Continue to next model
        else:
            print(f"DEBUG: No GEMINI_API_KEY found in environment for {ticker}")

    # Final fallback
    return {
        "summary": "Rule-based fallback used.",
        "technical_outlook": "N/A",
        "model_used": "SimpleAI-v1 (Deterministic)"
    }

@app.function(
    image=image,
    secrets=[modal.Secret.from_name("googlecloud-secret")]
)
def test_analysis():
    ticker = "GOOG"
    context = "Alphabet shares rise as analysts bullish on AI search integration."
    print(f"--- Testing Hybrid AI for {ticker} ---")
    result = generate_ai_analysis_logic(ticker, context)
    print(json.dumps(result, indent=2))

@app.local_entrypoint()
def main():
    test_analysis.remote()
