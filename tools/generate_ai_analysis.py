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
        # DEBUG: Check version
        try:
            import pkg_resources
            version = pkg_resources.get_distribution("google-generativeai").version
            print(f"DEBUG: google-generativeai version: {version}")
        except:
            print("DEBUG: Could not determine google-generativeai version")

        genai.configure(api_key=api_key)
        
        # DEBUG: List available models to see what the key actually sees
        print("DEBUG: Checking available models...")
        available_models = []
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
            print(f"DEBUG: Available models: {available_models}")
        except Exception as list_err:
            print(f"DEBUG: Failed to list models: {list_err}")

        # Try to use a model that likely exists in v1
        # If the list above showed names, we could pick one. 
        # For now, let's try the alias or full name.
        model_name = 'gemini-1.5-flash'
        if available_models and any('gemini-1.5-flash' in m for m in available_models):
            # Use the first one that matches
            model_name = [m for m in available_models if 'gemini-1.5-flash' in m][0]
            print(f"DEBUG: Using found model name: {model_name}")

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
