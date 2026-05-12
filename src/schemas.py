from pydantic import BaseModel

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