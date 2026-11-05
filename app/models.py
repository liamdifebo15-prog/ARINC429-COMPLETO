from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Instrumento(Base):
    __tablename__ = "instrumentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    etiqueta_octal: Mapped[str] = mapped_column(String(3), nullable=False)
    unidad: Mapped[str] = mapped_column(String(20), default="", nullable=False)
    valor_minimo: Mapped[float] = mapped_column(Float, nullable=False)
    valor_maximo: Mapped[float] = mapped_column(Float, nullable=False)
    escala_lsb: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    sdi: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ssm: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    envios: Mapped[list["Envio"]] = relationship(back_populates="instrumento")


class Envio(Base):
    __tablename__ = "envios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    instrumento_id: Mapped[int] = mapped_column(ForeignKey("instrumentos.id"), nullable=False)
    valor: Mapped[float] = mapped_column(Float, nullable=False)
    codigo_arinc429: Mapped[str] = mapped_column(String(8), nullable=False)
    estado_serial: Mapped[str] = mapped_column(String(30), default="simulado", nullable=False)
    estado_audio: Mapped[str] = mapped_column(String(30), default="simulado", nullable=False)
    detalle_salida: Mapped[str | None] = mapped_column(Text, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    instrumento: Mapped[Instrumento] = relationship(back_populates="envios")
