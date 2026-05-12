# Nistula Unified Messaging Platform

A backend system to normalize inbound guest messages from various channels, classify them, and generate contextual AI drafts using Claude.

## Tech Stack
*   **Python 3.10+**
*   **FastAPI** (High performance, excellent Pydantic validation)
*   **Anthropic SDK** 

## Setup Instructions

1. Clone the repository and navigate to the directory.
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   * Mac/Linux: `source venv/bin/activate`
   * Windows: `venv\Scripts\activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy the environment template: `cp .env.example .env`
6. Add your Claude API key to the `.env` file.
7. Start the server: `uvicorn src.main:app --reload`

The API will be available at `http://127.0.0.1:8000`. You can view the interactive Swagger documentation at `http://127.0.0.1:8000/docs`.

## Confidence Scoring Logic

The confidence score (0.0 to 1.0) is determined by instructing the LLM to evaluate its own ability to answer the query based **strictly on the provided property context**. 

*   **1.0 - 0.85 (auto_send):** The query directly matches facts in the context (e.g., standard check-in time at 2:00 PM, WiFi password, basic pricing).
*   **0.84 - 0.60 (agent_review):** The query requires slight extrapolation, or the guest has a complex multi-part question where some details are missing.
*   **< 0.60 (escalate):** The query involves information completely absent from the context, or it is a highly emotional/urgent `complaint` requiring human empathy and operational intervention (like maintenance at 3:00 AM). Note: Any message classified as a `complaint` is hardcoded to force the `escalate` action, regardless of the AI's raw confidence score.