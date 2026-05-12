import json
import re
from anthropic import Anthropic
from src.config import ANTHROPIC_API_KEY, CLAUDE_MODEL, PROPERTY_CONTEXT

client = Anthropic(api_key=ANTHROPIC_API_KEY)

def get_ai_draft(guest_name: str, message_text: str) -> dict:
    """Calls Claude API and returns a cleanly extracted JSON dictionary."""
    system_prompt = f"""You are an intelligent hospitality assistant for Nistula. 
    You will receive a guest message. Analyze it and output STRICTLY a JSON object with three keys:
    1. "query_type": Must be exactly one of: pre_sales_availability, pre_sales_pricing, post_sales_checkin, special_request, complaint, general_enquiry.
    2. "drafted_reply": A polite, helpful response using ONLY the provided property context.
    3. "confidence_score": A float between 0.0 and 1.0 indicating how fully the context answers the query.
    
    Property Context:
    {PROPERTY_CONTEXT}
    """

    user_prompt = f"Guest Name: {guest_name}\nMessage: {message_text}"

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=500,
        temperature=0.2,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )

    raw_text = response.content[0].text
    print(f"\n--- Raw Claude Output ---\n{raw_text}\n-------------------------\n")
    
    # Regex to extract JSON block safely
    match = re.search(r'\{.*\}', raw_text, re.DOTALL)
    if not match:
        raise ValueError("No JSON format detected in AI response")
        
    return json.loads(match.group(0))

def determine_action(score: float, query_type: str) -> str:
    """Business logic rules engine for message routing."""
    if query_type == "complaint":
        return "escalate"
    
    if score > 0.85:
        return "auto_send"
    elif score >= 0.60:
        return "agent_review"
    else:
        return "escalate"