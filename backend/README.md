# Backend

FastAPI backend for the learning Telegram bot.

- API: /api/
- Worker: Celery (for async processing like PDF ingestion, TTS)
- Database: placeholder (SQLAlchemy)

Run locally:

1. Create virtualenv: python -m venv .venv
2. Activate and install: .\.venv\Scripts\activate; pip install -r requirements.txt
3. Start: uvicorn backend.main:app --reload
