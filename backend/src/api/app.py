"""FastAPI app for the design backend.

Run from the backend folder:  uvicorn src.api.app:app --reload
Then open http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router

app = FastAPI(title='AI 3D Print Assistant - backend', version='0.2.0')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])
app.include_router(router)