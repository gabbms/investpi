import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, importacao, painel, usuarios, versoes
from app.config import settings, validar_producao

validar_producao(settings, os.environ)

app = FastAPI(title="Sistema ASG · Investe Piauí")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Publicações de teste da Vercel (um PR aberto) usam o mesmo banco do site oficial: nelas, só leitura.
GRAVA = {"POST", "PUT", "PATCH", "DELETE"}
LIVRES = {"/api/auth/login", "/api/painel/simular-pesos"}  # não gravam nada


@app.middleware("http")
async def so_leitura_em_teste(request: Request, call_next):
    if os.environ.get("VERCEL_ENV") == "preview" and request.method in GRAVA and request.url.path not in LIVRES:
        return JSONResponse(
            {"detail": "Esta é uma publicação de teste (PR): ela só lê os dados. Use o site oficial para gravar."},
            status_code=403,
        )
    return await call_next(request)


@app.get("/api/saude")
def saude() -> dict:
    return {"ok": True}


app.include_router(auth.router)
app.include_router(importacao.router)
app.include_router(versoes.router)
app.include_router(painel.router)
app.include_router(usuarios.router)
