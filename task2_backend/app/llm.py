import os
from dotenv import load_dotenv
import google.generativeai as genai

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

# ===============================
# Gemini Configuration
# ===============================
if api_key:
    genai.configure(api_key=api_key)
else:
    print("CRITICAL: GEMINI_API_KEY missing from environment")

def analyze_review(review_text: str):
    fallback_summary = "The customer shared general feedback without specific issues."
    fallback_action = "Monitor feedback trends and follow up if similar reviews increase."
    fallback_reply = "Thank you for taking the time to share your feedback with us. We truly appreciate it."

    if not api_key:
        return fallback_summary, fallback_action, fallback_reply

    try:
        model = genai.GenerativeModel("gemini-flash-latest")
        
        prompt = f"""
        Analyze the following customer review and provide:
        1. SUMMARY: A concise summary of the review.
        2. ACTION: A suggested business action based on the feedback.
        3. REPLY: A polite customer support reply.

        Review: "{review_text}"

        Format your response exactly as:
        SUMMARY: <text>
        ACTION: <text>
        REPLY: <text>
        """
        
        response = model.generate_content(prompt)
        text = response.text
        print(f"DEBUG: Gemini Response: {text}")

        # Initialize with defaults
        summary, action, reply = fallback_summary, fallback_action, fallback_reply

        if "SUMMARY:" in text:
            summary = text.split("SUMMARY:")[1].split("ACTION:")[0].strip()
        if "ACTION:" in text:
            action = text.split("ACTION:")[1].split("REPLY:")[0].strip()
        if "REPLY:" in text:
            reply = text.split("REPLY:")[1].strip()

        return summary, action, reply

    except Exception as e:
        print(f"LLM API Error: {e}")
        return fallback_summary, fallback_action, fallback_reply
