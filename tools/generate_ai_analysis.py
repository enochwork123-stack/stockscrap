import os
import json
import sys
import google.generativeai as genai

def generate_ai_analysis(ticker, news_context, price_context=""):
    """
    Generate AI news summary and technical outlook using Gemini API (SDK).
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {
            "summary": "AI Key not configured. Please add GEMINI_API_KEY to secrets.",
            "technical_outlook": "Technical analysis unavailable."
        }
    
    try:
        # Standardize on SDK which handles endpoint versions correctly
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        
        # Based on diagnostic run, gemini-2.0-flash is available and 1.5-flash is not.
        model_name = 'gemini-2.0-flash'
        
        print(f"DEBUG: Using verified model: {model_name}")
        model = genai.GenerativeModel(model_name)
        
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

        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
            ),
        )
        
        # Parse the JSON response
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            # Fallback regex for when AI wraps in markdown blocks
            import re
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                return json.loads(match.group())
            raise Exception("Failed to parse AI JSON response")

    except Exception as e:
        print(f"Error generating AI analysis for {ticker}: {e}")
        return {
            "summary": f"AI Error: {str(e)[:100]}",
            "technical_outlook": "Analysis failed. See logs."
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No ticker provided"}))
        sys.exit(1)
    
    ticker = sys.argv[1]
    news = sys.argv[2] if len(sys.argv) > 2 else ""
    print(json.dumps(generate_ai_analysis(ticker, news)))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No ticker provided"}))
        sys.exit(1)
    
    ticker = sys.argv[1]
    news = sys.argv[2] if len(sys.argv) > 2 else ""
    print(json.dumps(generate_ai_analysis(ticker, news)))
