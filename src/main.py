import os
import uuid
import json
import re  # Added for regex extraction
from datetime import datetime
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from anthropic import Anthropic, APIError
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Nistula Webhook API")

# Initialize Anthropic client
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# --- Models ---

class InboundPayload(BaseModel):
    source: str
    guest_name: str
    message: str
    timestamp: str
    booking_ref: str
    property_id: str

class WebhookResponse(BaseModel):
    message_id: str
    query_type: str
    drafted_reply: str
    confidence_score: float
    action: str

# --- Mock Context ---

PROPERTY_CONTEXT = """
Property: Villa B1, Assagao, North Goa
Bedrooms: 3 | Max guests: 6 | Private pool: Yes
Check-in: 2:00 PM | Check-out: 11:00 AM
Base rate: INR 18,000 per night (up to 4 guests)
Extra guest: INR 2,000 per night per person
WiFi password: Nistula@2024
Caretaker: Available 8:00 AM to 10:00 PM
Chef on call: Yes, pre-booking required
Availability April 20-24: Available
Cancellation: Free up to 7 days before check-in
"""

def determine_action(score: float, query_type: str) -> str:
    """Business logic for routing the message."""
    if query_type == "complaint":
        return "escalate"
    
    if score > 0.85:
        return "auto_send"
    elif score >= 0.60:
        return "agent_review"
    else:
        return "escalate"

@app.post("/webhook/message", response_model=WebhookResponse)
async def handle_message(payload: InboundPayload):
    try:
        # 1. Normalize Schema
        message_id = str(uuid.uuid4())
        normalized_data = {
            "message_id": message_id,
            "source": payload.source,
            "guest_name": payload.guest_name,
            "message_text": payload.message,
            "timestamp": payload.timestamp,
            "booking_ref": payload.booking_ref,
            "property_id": payload.property_id
        }

        # 2. Construct AI Prompt
        system_prompt = f"""You are an intelligent hospitality assistant for Nistula. 
        You will receive a guest message. Analyze it and output STRICTLY a JSON object with three keys:
        1. "query_type": Must be exactly one of: pre_sales_availability, pre_sales_pricing, post_sales_checkin, special_request, complaint, general_enquiry.
        2. "drafted_reply": A polite, helpful response using ONLY the provided property context.
        3. "confidence_score": A float between 0.0 and 1.0 indicating how fully the property context answers the query.
        
        Property Context:
        {PROPERTY_CONTEXT}
        """

        user_prompt = f"Guest Name: {normalized_data['guest_name']}\nMessage: {normalized_data['message_text']}"

        # 3. Call Claude API
        response = anthropic_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=500,
            temperature=0.2,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )

        # 4. Parse AI Response (UPDATED WITH REGEX EXTRACTION)
        try:
            raw_text = response.content[0].text
            print(f"\n--- Raw Claude Output ---\n{raw_text}\n-------------------------\n")
            
            # Find everything between the first { and last }
            match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if not match:
                raise ValueError("No JSON format detected in AI response")
                
            clean_json = match.group(0)
            ai_output = json.loads(clean_json)
            
            query_type = ai_output.get("query_type", "general_enquiry")
            drafted_reply = ai_output.get("drafted_reply", "Thank you for your message. An agent will be with you shortly.")
            confidence_score = float(ai_output.get("confidence_score", 0.0))
            
        except (json.JSONDecodeError, IndexError, ValueError, AttributeError) as e:
            print(f"JSON Parsing Error: {e}")
            query_type = "general_enquiry"
            drafted_reply = "We have received your message and will reply shortly."
            confidence_score = 0.0

        # 5. Determine Routing Action
        action = determine_action(confidence_score, query_type)

        # 6. Return response
        return WebhookResponse(
            message_id=message_id,
            query_type=query_type,
            drafted_reply=drafted_reply,
            confidence_score=confidence_score,
            action=action
        )

    except APIError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"AI Service Error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {str(e)}")