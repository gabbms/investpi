from collections.abc import Mapping
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

RAIZ_BACKEND = Path(__file__).resolve().parent.parent
RAIZ_PROJETO = RAIZ_BACKEND.parent
SEGREDO_PADRAO = "troque-este-segredo-por-um-texto-longo-e-aleatorio"


def normalizar_url_banco(url: str) -> str:
    """Troca o esquema "postgres://" ou "postgresql://" (como a Neon entrega) pelo driver do projeto."""
    for prefixo in ("postgres://", "postgresql://"):
        if url.startswith(prefixo):
            return "postgresql+psycopg://" + url[len(prefixo):]
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=RAIZ_PROJETO / ".env", extra="ignore")

    DATABASE_URL: str = "postgresql+psycopg://asg:asg@localhost:5433/asg"
    TEST_DATABASE_URL: str = "postgresql+psycopg://asg:asg@localhost:5433/asg_test"
    JWT_SEGREDO: str = SEGREDO_PADRAO
    JWT_HORAS: float = 8
    ADMIN_EMAIL: str | None = None
    ADMIN_SENHA: str | None = None
    LEITOR_EMAIL: str | None = None
    LEITOR_SENHA: str | None = None
    CAMINHO_MODELO: str = "dados/base_modelo.xlsx"

    @field_validator("DATABASE_URL", "TEST_DATABASE_URL")
    @classmethod
    def _driver_psycopg(cls, v: str) -> str:
        return normalizar_url_banco(v)

    @property
    def caminho_modelo(self) -> Path:
        p = Path(self.CAMINHO_MODELO)
        return p if p.is_absolute() else RAIZ_BACKEND / p


def validar_producao(s: Settings, ambiente: Mapping[str, str]) -> None:
    """Na Vercel, recusa subir com o segredo de login padrão (público no repositório) ou curto demais."""
    if ambiente.get("VERCEL") and (s.JWT_SEGREDO == SEGREDO_PADRAO or len(s.JWT_SEGREDO) < 32):
        raise RuntimeError("Defina JWT_SEGREDO (32+ caracteres aleatórios) nas variáveis de ambiente da Vercel.")


settings = Settings()
