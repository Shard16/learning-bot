# PowerShell script to run backend and bot locally (development)
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r backend/requirements.txt; Start-Process -NoNewWindow -FilePath python -ArgumentList "-m", "uvicorn", "backend.main:app", "--reload"
