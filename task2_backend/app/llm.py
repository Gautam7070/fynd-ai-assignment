import os
import json
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel

# ===============================
# Load .env safely
# ===============================
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.abspath(os.path.join(current_dir, "..", ".env"))
load_dotenv(env_path)

# Secondary check for repo root
if not os.getenv("GEMINI_API_KEY"):
    repo_root_env = os.path.abspath(os.path.join(current_dir, "..", "..", ".env"))
    load_dotenv(repo_root_env)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("CRITICAL: GEMINI_API_KEY missing from environment")

# ===============================
# Gemini Client (NEW SDK)
# ===============================
client = genai.Client(api_key=api_key) if api_key else None


class AnalysisResult(BaseModel):
    summary: str
    action: str
    reply: str


# ===============================
# Analyze Review (RATING-AWARE)
# ===============================
def analyze_review(review: str, rating: int):
    # Dynamic and varied fallbacks based on rating
    if rating <= 2:
        fallback_summary = f"Customer expressed dissatisfaction (Rating: {rating})."
        fallback_action = "Investigate the specific issue mentioned in the review and follow up."
        fallback_reply = "We're sorry to hear about your experience. We are looking into this to improve."
    elif rating == 3:
        fallback_summary = f"Customer provided neutral/mixed feedback (Rating: {rating})."
        fallback_action = "Monitor feedback trends and look for specific areas to improve."
        fallback_reply = "Thank you for your feedback. We appreciate your honesty and will work to improve."
    else:
        fallback_summary = f"Customer had a positive experience (Rating: {rating})."
        fallback_action = "Maintain current quality standards and thank the customer."
        fallback_reply = "We're so glad you enjoyed your experience! Thank you for the kind words."

    if not client:
        return fallback_summary, fallback_action, fallback_reply

    # 🎯 Tone/Intent based on rating
    if rating <= 2:
        tone = "apologetic and empathetic"
        intent = "Apologize sincerely, acknowledge the issue specifically from the review, and assure improvement."
    elif rating == 3:
        tone = "neutral and professional"
        intent = "Thank the customer, acknowledge mixed feedback, and show openness to improvement."
    else:
        tone = "positive and enthusiastic"
        intent = "Thank the customer warmly, reinforce positive points from the review, and encourage return."

    try:
        prompt = f"""
You are an intelligent customer feedback analysis AI. 

Input:
Rating: {rating} stars
Review: "{review}"

Tone: {tone}
Intent: {intent}

Task:
1. summary: A concise, specific sentence summarizing the sentiment and key details from this specific review. AVOID generic summaries.
2. action: One clear, actionable business step based ONLY on this specific review.
3. reply: A short, human-like response matching the tone and addressing the review content.

Output must be valid JSON matching the schema.
"""

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'response_schema': AnalysisResult,
            }
        )

        if not response.text:
            return fallback_summary, fallback_action, fallback_reply

        data = json.loads(response.text)
        summary = data.get("summary", fallback_summary)
        action = data.get("action", fallback_action)
        reply = data.get("reply", fallback_reply)

        return summary, action, reply

    except Exception as e:
        print(f"LLM API Error: {e}")
        # Try a simpler fallback for summary to avoid repeating the exact same message
        if rating <= 2:
             summary = f"Negative feedback received: '{review[:30]}...'"
        elif rating == 3:
             summary = f"Neutral feedback received: '{review[:30]}...'"
        else:
             summary = f"Positive feedback received: '{review[:30]}...'"
        
        return summary, fallback_action, fallback_reply
