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

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
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

    try:
        response = requests.post(url, json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }, timeout=30)
        
        if response.status_code != 200:
            print(f"Gemini API Error ({response.status_code}): {response.text}")
            raise Exception(f"API returned {response.status_code}")
            
        result = response.json()
        if 'candidates' not in result:
            print(f"Unexpected Gemini Response Structure: {result}")
            raise Exception("No candidates in response")
            
        content = result['candidates'][0]['content']['parts'][0]['text']
        return json.loads(content)
    except Exception as e:
        error_msg = str(e)[:100]
        print(f"Error generating AI analysis for {ticker}: {e}")
        return {
            "summary": f"AI Error: {error_msg}",
            "technical_outlook": "Check logs for technical error."
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No ticker provided"}))
        sys.exit(1)
    
    ticker = sys.argv[1]
    news = sys.argv[2] if len(sys.argv) > 2 else ""
    print(json.dumps(generate_ai_analysis(ticker, news)))
