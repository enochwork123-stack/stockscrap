import json
import os
import time

def generate_ai_analysis(ticker, news_context, price_context=""):
    """
    Hybrid Intelligence Engine.
    - GOOG: Gemini-powered deep analysis (100-200 words).
    - Others: Deterministic Rule-Based Engine (Fast & Reliable).
    """
    
    # 1. Branch for Gemini (GOOG only)
    if ticker == "GOOG":
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                
                # Verified working model from diagnostics
                model = genai.GenerativeModel('gemini-2.0-flash')
                
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
                return {
                    "summary": data.get("summary", ""),
                    "technical_outlook": data.get("technical_outlook", ""),
                    "model_used": "Gemini-2.0-Flash (Advanced)"
                }
            except Exception as e:
                print(f"DEBUG: Gemini failed for GOOG, falling back to rule-based: {e}")
                # Fall through to rule-based if Gemini fails (Stability first)
        else:
            print("DEBUG: Gemini API Key not found for GOOG, using rule-based.")

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
