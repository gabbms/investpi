from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

RAIZ_BACKEND = Path(__file__).resolve().parent.parent
RAIZ_PROJETO = RAIZ_BACKEND.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=RAIZ_PROJETO / ".env", extra="ignore")

    DATABASE_URL: str = "postgresql+psycopg://asg:asg@localhost:5433/asg"
    TEST_DATABASE_URL: str = "postgresql+psycopg://asg:asg@localhost:5433/asg_test"
    JWT_SEGREDO: str = "troque-este-segredo"
    JWT_HORAS: float = 8
    ADMIN_EMAIL: str | None = None
    ADMIN_SENHA: str | None = None
    LEITOR_EMAIL: str | None = None
    LEITOR_SENHA: str | None = None
    CAMINHO_MODELO: str = "dados/base_modelo.xlsx"

    @property
    def caminho_modelo(self) -> Path:
        p = Path(self.CAMINHO_MODELO)
        return p if p.is_absolute() else RAIZ_BACKEND / p


settings = Settings()
