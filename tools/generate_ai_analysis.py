import json
import os
import time

def generate_ai_analysis(ticker, news_context, price_context="", llm_inference_handle=None):
    """
    Hybrid Intelligence Engine.
    - GOOG: Gemini-powered deep analysis (100-200 words).
    - Others: Deterministic Rule-Based Engine (Fast & Reliable).
    """
    
    # 1. Branch for Internal Modal LLM (GOOG only)
    if ticker == "GOOG":
        try:
            import modal
            print(f"DEBUG: Attempting Internal Modal LLM call for {ticker}...")
            
            # Use direct handle if provided, otherwise from_name
            if llm_inference_handle:
                llm_fn = llm_inference_handle
            else:
                # Use correct from_name syntax for deployed apps
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
            
            # Extract JSON if the model wrapped it in markdown or text
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                print(f"DEBUG: Successfully received Modal LLM response for {ticker}")
                return {
                    "summary": data.get("summary", ""),
                    "technical_outlook": data.get("technical_outlook", ""),
                    "model_used": "Modal-OSS-LLM (Llama/Qwen)"
                }
            else:
                # If it's just raw text, split it simply or use it as summary
                return {
                    "summary": response_text[:1000], 
                    "technical_outlook": "See summary for details.",
                    "model_used": "Modal-OSS-LLM (Raw Text)"
                }
                
        except Exception as e:
            print(f"DEBUG: Internal LLM failed for {ticker}. Error: {str(e)}")
            # Fall through to rule-based fallback

    # 2. Rule-Based Engine (Fallback for GOOG or Default for others)
    # Keyword-based sentiment weights
    BULLISH_KEYWORDS = ["surge", "growth", "buy", "partnership", "beat", "rally", "profit", "expansion", "positive", "high", "upgrade"]
    BEARISH_KEYWORDS = ["drop", "loss", "decline", "sell", "miss", "risk", "debt", "lower", "negative", "slump", "downgrade"]
    
    context_lower = (news_context + " " + ticker).lower()
    
    bull_count = sum(1 for word in BULLISH_KEYWORDS if word in context_lower)
    bear_count = sum(1 for word in BEARISH_KEYWORDS if word in context_lower)
    
    sentiment = "neutral"
    if bull_count > bear_count:
        sentiment = "bullish"
    elif bear_count > bull_count:
        sentiment = "bearish"
        
    if sentiment == "bullish":
        summary = f"Recent activity for {ticker} shows a strong bullish bias, supported by positive news flow highlighting growth and potential catalysts. Market participants are focusing on expansionary themes and robust underlying fundamentals."
    elif sentiment == "bearish":
        summary = f"The current news flow for {ticker} reflects a cautious to bearish sentiment, as headlines focus on potential risks or downward pressure. Investors are weighing recent declines and negative catalysts in the short-term outlook."
    else:
        summary = f"{ticker} is currently seeing balanced news coverage with a mix of neutral indicators. The market appears to be in a consolidation phase as it digests recent data points without a clear directional bias."

    if sentiment == "bullish":
        outlook = f"Technical indicators suggest continued upward momentum. If the price sustains above key moving averages, the next resistance levels could be challenged in the coming sessions."
    elif sentiment == "bearish":
        outlook = f"The technical chart shows vulnerability to further downside. Failure to hold psychological support levels may lead to a deeper retracement before stabilization occurs."
    else:
        outlook = f"Technicals indicate a range-bound environment. A decisive breakout above or below established support/resistance zones is needed to confirm the next major trend."

    return {
        "summary": summary,
        "technical_outlook": outlook,
        "model_used": "SimpleAI-v1 (Deterministic)"
    }

if __name__ == "__main__":
    # Test GOOG (GEMINI_API_KEY must be set in env)
    print("Testing GOOG Hybrid Analysis...")
    print(json.dumps(generate_ai_analysis("GOOG", "Alphabet reports record profits and cloud acceleration."), indent=2))
    
    print("\nTesting BTC Rule-Based Analysis...")
    print(json.dumps(generate_ai_analysis("BTC", "Bitcoin faces regulatory hurdles in Europe."), indent=2))
