from fastapi import FastAPI

from src.api.routes import router

#@app je decorator alias handler pre post
app = FastAPI(
    title="PSR Lens API",
    description="API for phishing message analysis.",
    version="0.1.0",
)

app.include_router(router)