import modal
import os
import json
import re

app = modal.App("test-hybrid-direct")

image = (
    modal.Image.debian_slim()
    .pip_install("modal")
)

def generate_ai_analysis_logic(ticker, news_context, price_context=""):
    """
    Hybrid Intelligence Engine logic using Internal Modal LLM.
    """
    if ticker == "GOOG":
        try:
            import modal
            print(f"DEBUG: Attempting Internal Modal LLM call for {ticker}...")
            
            # Use correct from_name syntax
            llm_fn = modal.Function.from_name("stockscrap-portfolio-sync", "llm_inference")
            
            prompt = f"""
            Based on the news headlines provided below for {ticker}, 
            please provide a 100-200 word sentimental analysis summary. 
            Focus on themes, investor sentiment, and potential market impact.
            
            Keep the TECHNICAL_OUTLOOK concise (2-3 sentences).
            
            NEWS HEADLINES:
            {news_context}
            
            PRICE CONTEXT:
            {price_context}
            
            IMPORTANT: Return ONLY a raw JSON object with these keys: "summary" and "technical_outlook".
            """
            
            response_text = llm_fn.remote(prompt)
            print(f"DEBUG: Raw response from LLM: {response_text[:100]}...")
            
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return {
                    "summary": data.get("summary", ""),
                    "technical_outlook": data.get("technical_outlook", ""),
                    "model_used": "Modal-OSS-LLM (Qwen-2.5)"
                }
            else:
                return {
                    "summary": response_text[:1000], 
                    "technical_outlook": "See summary for details.",
                    "model_used": "Modal-OSS-LLM (Raw Text)"
                }
                
        except Exception as e:
            print(f"DEBUG: Internal LLM failed for {ticker}. Error: {str(e)}")

    # Rule-based fallback
    return {
        "summary": "Rule-based fallback used.",
        "technical_outlook": "N/A",
        "model_used": "SimpleAI-v1 (Deterministic)"
    }

@app.function(
    image=image
)
def test_analysis():
    ticker = "GOOG"
    context = "Alphabet shares rise as analysts bullish on AI search integration. Google Cloud shows triple digit growth."
    print(f"--- Testing Hybrid AI for {ticker} ---")
    result = generate_ai_analysis_logic(ticker, context)
    print(json.dumps(result, indent=2))

@app.local_entrypoint()
def main():
    test_analysis.remote()
