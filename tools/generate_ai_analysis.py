#!/usr/bin/env python3
import os
import json
import requests
import sys

def generate_ai_analysis(ticker, news_context, price_context=""):
    """
    Generate AI news summary and technical outlook using Gemini API.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {
            "summary": "AI Key not configured. Please add GEMINI_API_KEY to secrets.",
            "technical_outlook": "Technical analysis unavailable."
        }
    
    # Extra debug logic for key format
    key_info = f"len={len(api_key)}, prefix={api_key[:4]}"
    print(f"DEBUG: Using key: {key_info}")
    
    # Try different models and versions
    variants = [
        ("v1", "gemini-1.5-flash"),
        ("v1", "gemini-1.5-pro"),
        ("v1beta", "gemini-1.5-flash"),
        ("v1beta", "gemini-pro")
    ]
    
    prompt = f"""
    You are a senior financial analyst. Analyze the following data for {ticker} and provide two short sections:
    1. NEWS_PULSE: A 2-3 sentence summary of the themes in the recent headlines.
    2. TECHNICAL_OUTLOOK: A 2-3 sentence outlook based on typical price action (if provided).
    
    Keep it professional, concise, and objective. Use plain text only.
    
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

    last_error = "Unknown error"
    
    for version, model in variants:
        try:
            url = f"https://generativelanguage.googleapis.com/{version}/models/{model}:generateContent?key={api_key}"
            response = requests.post(url, json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"response_mime_type": "application/json"}
            }, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result['candidates'][0]['content']['parts'][0]['text']
                return json.loads(content)
            else:
                last_error = f"{version}/{model} failed ({response.status_code})"
                if response.status_code == 404:
                    continue
        except Exception as e:
            last_error = str(e)
            continue

    return {
        "summary": f"AI Error: {last_error}",
        "technical_outlook": "Check API key and project settings."
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No ticker provided"}))
        sys.exit(1)
    
    ticker = sys.argv[1]
    news = sys.argv[2] if len(sys.argv) > 2 else ""
    print(json.dumps(generate_ai_analysis(ticker, news)))
