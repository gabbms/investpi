from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, importacao, painel, usuarios, versoes

app = FastAPI(title="Sistema ASG · Investe Piauí")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/saude")
def saude() -> dict:
    return {"ok": True}


app.include_router(auth.router)
app.include_router(importacao.router)
app.include_router(versoes.router)
app.include_router(painel.router)
app.include_router(usuarios.router)
