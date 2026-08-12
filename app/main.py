from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.core.config import settings
from app.core.audio import ensure_audio_dir_exists

from contextlib import asynccontextmanager
from app.core.database import SessionLocal
from app.core.seed import seed_admin_user

# Routers
from app.routers.auth import router as auth_router
from app.routers.usuario import router as usuario_router
from app.routers.candidato import router as candidato_router
from app.routers.vaga import router as vaga_router
from app.routers.candidatura import router as candidatura_router
from app.routers.entrevista import router as entrevista_router
from app.routers.audio import router as audio_router

# Garantir que o diretório de áudio exista ao iniciar
ensure_audio_dir_exists()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Popular usuário admin no banco na inicialização
    db = SessionLocal()
    try:
        seed_admin_user(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="VoiceMatch AI Backend",
    description="API do sistema de recrutamento com análise de áudio",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar pasta de áudios estáticos para serem servidos
app.mount("/media", StaticFiles(directory="media"), name="media")

# Include Routers
app.include_router(auth_router)
app.include_router(usuario_router)
app.include_router(candidato_router)
app.include_router(vaga_router)
app.include_router(candidatura_router)
app.include_router(entrevista_router)
app.include_router(audio_router)


@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    try:
        # Tenta executar uma consulta simples no banco
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro de conexão com o banco de dados: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
