from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.models.helpers.model_registry import download_model_registry
from src.serve.routers import health_router, prediction_router

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(prediction_router)

@app.on_event("startup")
async def startup_event():
    download_model_registry()

@app.get("/")
def root():
    return {"message": "Hello, FastAPI!"}

# RUN -> uvicorn main:app --reload
# RUN in root -> uvicorn src.serve.main:app --reload --port 8000