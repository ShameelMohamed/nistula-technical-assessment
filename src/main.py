import uuid
from fastapi import FastAPI, HTTPException, status
from anthropic import APIError
from src.schemas import InboundPayload, WebhookResponse
from src.ai_service import get_ai_draft, determine_action

app = FastAPI(title="Nistula Webhook API")

@app.post("/webhook/message", response_model=WebhookResponse)
async def handle_message(payload: InboundPayload):
    try:
        # 1. Generate unique ID
        message_id = str(uuid.uuid4())

        # 2. Get AI Classification & Draft
        try:
            ai_output = get_ai_draft(payload.guest_name, payload.message)
            query_type = ai_output.get("query_type", "general_enquiry")
            drafted_reply = ai_output.get("drafted_reply", "Thank you for your message.")
            confidence_score = float(ai_output.get("confidence_score", 0.0))
        except Exception as e:
            print(f"AI Parsing Fallback: {e}")
            query_type = "general_enquiry"
            drafted_reply = "We have received your message and will reply shortly."
            confidence_score = 0.0

        # 3. Apply Routing Rules
        action = determine_action(confidence_score, query_type)

        # 4. Return Normalized Schema
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