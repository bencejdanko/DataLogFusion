"""
main.py
-------
DataLogFusion Backend — Entry Point

Runs the consumer API server (FastAPI + uvicorn).
The API reads live data from Redis Cloud and serves it to the dashboard.

Usage:
  python main.py
  # or directly:
  uvicorn api:app --host 0.0.0.0 --port 8000 --reload
"""

import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))

    print(f"Starting DataLogFusion API on http://{host}:{port}")
    print("  GET /health    — Redis health check")
    print("  GET /latest    — latest sensor snapshot")
    print("  GET /history   — recent readings")
    print("  GET /stream    — live SSE feed")

    uvicorn.run("api:app", host=host, port=port, reload=False, log_level="info")
