from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def agora() -> datetime:
    return datetime.now(timezone.utc)


class Usuario(Base):
    __tablename__ = "usuario"
    __table_args__ = (CheckConstraint("perfil in ('admin','leitor')", name="ck_usuario_perfil"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    nome: Mapped[str] = mapped_column(String(255))
    senha_hash: Mapped[str] = mapped_column(String(255))
    perfil: Mapped[str] = mapped_column(String(10))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)


class Versao(Base):
    __tablename__ = "versao"
    __table_args__ = (
        CheckConstraint("status in ('ativa','inativa','rejeitada')", name="ck_versao_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[int] = mapped_column(Integer, unique=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    enviado_por_id: Mapped[int | None] = mapped_column(ForeignKey("usuario.id"), nullable=True)
    nome_arquivo: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(10))
    linhas_por_aba: Mapped[dict] = mapped_column(JSONB, default=dict)
    avisos: Mapped[list] = mapped_column(JSONB, default=list)
    erros: Mapped[list] = mapped_column(JSONB, default=list)

    enviado_por: Mapped[Usuario | None] = relationship()


class LinhaDado(Base):
    __tablename__ = "linha_dado"

    id: Mapped[int] = mapped_column(primary_key=True)
    versao_id: Mapped[int] = mapped_column(ForeignKey("versao.id", ondelete="CASCADE"), index=True)
    aba: Mapped[str] = mapped_column(String(64), index=True)
    dados: Mapped[dict] = mapped_column(JSONB)
