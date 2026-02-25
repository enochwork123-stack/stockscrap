import json
import os

def generate_ai_analysis(ticker, news_context, price_context=""):
    """
    Deterministic Rule-Based Intelligence Engine.
    Replaces Gemini API to ensure 100% reliability and zero latency.
    """
    
    # Keyword-based sentiment weights
    BULLISH_KEYWORDS = ["surge", "growth", "buy", "partnership", "beat", "rally", "profit", "expansion", "positive", "high", "upgrade"]
    BEARISH_KEYWORDS = ["drop", "loss", "decline", "sell", "miss", "risk", "debt", "lower", "negative", "slump", "downgrade"]
    
    context_lower = (news_context + " " + ticker).lower()
    
    bull_count = sum(1 for word in BULLISH_KEYWORDS if word in context_lower)
    bear_count = sum(1 for word in BEARISH_KEYWORDS if word in context_lower)
    
    # Determine Sentiment Tone
    sentiment = "neutral"
    if bull_count > bear_count:
        sentiment = "bullish"
    elif bear_count > bull_count:
        sentiment = "bearish"
        
    # Generate News Pulse (2-3 sentences)
    if sentiment == "bullish":
        summary = f"Recent activity for {ticker} shows a strong bullish bias, supported by positive news flow highlighting growth and potential catalysts. Market participants are focusing on expansionary themes and robust underlying fundamentals."
    elif sentiment == "bearish":
        summary = f"The current news flow for {ticker} reflects a cautious to bearish sentiment, as headlines focus on potential risks or downward pressure. Investors are weighing recent declines and negative catalysts in the short-term outlook."
    else:
        summary = f"{ticker} is currently seeing balanced news coverage with a mix of neutral indicators. The market appears to be in a consolidation phase as it digests recent data points without a clear directional bias."

    # Generate Technical Outlook
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
    # Test
    test_context = "Google reports surge in AI profit and new partnership with Apple."
    print(json.dumps(generate_ai_analysis("GOOG", test_context), indent=2))
