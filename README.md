# Nistula Guest Message Handler

FastAPI backend for the Nistula technical assessment. It accepts guest messages at `POST /webhook/message`, classifies the query, generates a contextual reply using Claude 3.5 Sonnet, and returns the drafted reply with an AI-generated confidence score and routing action.

---

# Setup

We use standard Python virtual environments and `pip` for dependency management.

## Install Dependencies

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
```

---

## Configure Environment Variables

Add the assessment API key to your `.env` file:

```env
ANTHROPIC_API_KEY=your-key-here
```

---

## Run the API

```bash
uvicorn src.main:app --reload --port 8000
```

---

# Example Request

You can test the endpoint using the interactive Swagger UI at:

```text
http://127.0.0.1:8000/docs
```

Or via cURL:

```bash
curl -X POST http://127.0.0.1:8000/webhook/message \
  -H "Content-Type: application/json" \
  -d '{
    "source": "whatsapp",
    "guest_name": "Rahul Sharma",
    "message": "Is the villa available from April 20 to 24? What is the rate for 2 adults?",
    "timestamp": "2026-05-05T10:30:00Z",
    "booking_ref": "NIS-2024-0891",
    "property_id": "villa-b1"
  }'
```

---

# Project Structure

```text
├── src/
│   ├── main.py        # Core FastAPI app and webhook router
│   ├── schemas.py     # Pydantic request/response models
│   ├── ai_service.py  # Claude API calls, JSON extraction, and business logic
│   └── config.py      # Environment loading and mock Villa B1 context
├── .env.example       # Environment variable template
├── requirements.txt   # Python dependencies
├── schema.sql         # PostgreSQL schema for Part 2
└── thinking.md        # Written answers for Part 3
```

---

# Main Design Choices

## Robust JSON Extraction

LLMs occasionally wrap JSON in markdown blocks or add conversational text. The `ai_service.py` implementation uses a regex extraction layer to ensure the API never crashes due to LLM formatting hallucinations.

## Separation of Concerns

The backend is split into dedicated files for configuration, routing, schemas, and external services. This modular architecture prevents business logic from tangling with API routing, making the codebase scalable and easy to test.

## Abstracted Identity Resolution (DB Schema)

Instead of strictly tying a channel source to a guest, the database schema introduces a `conversations` layer. This allows a guest to message via WhatsApp today and Airbnb tomorrow, successfully tying all cross-platform interactions back to a single unified `guest_id`.

---

# Confidence Scoring Logic

The confidence score (`0.0` to `1.0`) is determined dynamically by instructing Claude to evaluate its own ability to answer the query based strictly on the provided property context.

> **Note on Complaints:** Any message flagged by the AI as a `complaint` triggers an immediate bypass of the confidence score, hardcoding the action to `escalate` to ensure human intervention and protect the guest experience.

---

# Action Mapping

Based on the final AI confidence score, the system routes the message as follows:

| Score Range | Action | Routing Criteria |
| --- | --- | --- |
| `> 0.85` | `auto_send` | The query directly matches facts in the context (e.g., standard check-in time, base rates). |
| `0.60` to `0.85` | `agent_review` | The query requires slight extrapolation, or the guest has a multi-part question with partial context. |
| `< 0.60` (or `complaint`) | `escalate` | The query involves information entirely absent from the provided property context. |
