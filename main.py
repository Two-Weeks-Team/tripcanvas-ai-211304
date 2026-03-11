import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from routes import router

app = FastAPI()

@app.middleware("http")
async def normalize_api_prefix(request: Request, call_next):
    if request.scope.get("path", "").startswith("/api/"):
        request.scope["path"] = request.scope["path"][4:] or "/"
    return await call_next(request)

app.include_router(router)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def root():
    html = """
    <html><head><title>TripCanvas AI</title></head>
    <body style='background:#111;color:#eee;font-family:Arial;padding:2rem;'>
    <h1>TripCanvas AI</h1>
    <p>Turn your travel ideas into a visual canvas – AI‑crafted itineraries, budgets, and moodboards, all in one place.</p>
    <h2>Available Endpoints</h2>
    <ul>
      <li><b>GET /health</b> – health check</li>
      <li><b>POST /plan</b> – generate trip brief (expects {"query": "...", "preferences": {...}})</li>
      <li><b>POST /insights</b> – get insights for a selection (expects {"selection": "...", "context": {...}})</li>
    </ul>
    <h2>Tech Stack</h2>
    <ul>
      <li>FastAPI 0.115.0</li>
      <li>Python 3.12+</li>
      <li>PostgreSQL via SQLAlchemy 2.0.35</li>
      <li>DigitalOcean Serverless Inference (openai-gpt-oss-120b)</li>
    </ul>
    <p><a href="/docs" style='color:#0af;'>OpenAPI Docs</a> | <a href="/redoc" style='color:#0af;'>ReDoc</a></p>
    </body></html>
    """
    return HTMLResponse(content=html)
