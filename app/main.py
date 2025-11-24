from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="ChatBot Service API",
    description="Maneja las interacciones del bot de Telegram y la lógica de negocio."
)

app.include_router(router)

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
