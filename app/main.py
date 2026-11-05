import logging
import os
from collections.abc import Generator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.arinc429 import generar_palabra_bnr
from app.db import Base, SessionLocal, engine
from app.io_devices import SalidaHardware
from app.models import Envio, Instrumento


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.scalar(select(Instrumento.id).limit(1)) is None:
            db.add_all(
                [
                    Instrumento(nombre="Altitud", etiqueta_octal="203", unidad="ft", valor_minimo=-1000, valor_maximo=60000, escala_lsb=1.0),
                    Instrumento(nombre="Velocidad", etiqueta_octal="206", unidad="kt", valor_minimo=0, valor_maximo=1000, escala_lsb=1.0),
                    Instrumento(nombre="Temperatura", etiqueta_octal="213", unidad="°C", valor_minimo=-100, valor_maximo=200, escala_lsb=0.1),
                ]
            )
            db.commit()
    yield


app = FastAPI(title="Administrador de envíos ARINC 429", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class EnvioCrear(BaseModel):
    instrumento_id: int
    valor: float


class EnvioActualizar(BaseModel):
    instrumento_id: int
    valor: float


class InstrumentoSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    etiqueta_octal: str
    unidad: str
    valor_minimo: float
    valor_maximo: float
    escala_lsb: float


class EnvioSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    instrumento_id: int
    valor: float
    codigo_arinc429: str
    estado_serial: str
    estado_audio: str
    detalle_salida: str | None
    creado_en: str
    instrumento: InstrumentoSalida


def a_salida(envio: Envio) -> dict:
    return {
        "id": envio.id,
        "instrumento_id": envio.instrumento_id,
        "valor": envio.valor,
        "codigo_arinc429": envio.codigo_arinc429,
        "estado_serial": envio.estado_serial,
        "estado_audio": envio.estado_audio,
        "detalle_salida": envio.detalle_salida,
        "creado_en": envio.creado_en.isoformat() if envio.creado_en else "",
        "instrumento": envio.instrumento,
    }


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def inicio(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/api/instrumentos", response_model=list[InstrumentoSalida])
def listar_instrumentos(db: Session = Depends(get_db)):
    return db.scalars(select(Instrumento).order_by(Instrumento.nombre)).all()


@app.post("/api/envios", response_model=EnvioSalida, status_code=status.HTTP_201_CREATED)
def crear_envio(datos: EnvioCrear, db: Session = Depends(get_db)):
    instrumento = db.get(Instrumento, datos.instrumento_id)
    if instrumento is None:
        raise HTTPException(status_code=404, detail="Instrumento no encontrado")
    if not instrumento.valor_minimo <= datos.valor <= instrumento.valor_maximo:
        raise HTTPException(status_code=422, detail="El valor está fuera del rango del instrumento")

    try:
        palabra = generar_palabra_bnr(
            etiqueta_octal=instrumento.etiqueta_octal,
            valor=datos.valor,
            escala_lsb=instrumento.escala_lsb,
            sdi=instrumento.sdi,
            ssm=instrumento.ssm,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    envio = Envio(
        instrumento_id=instrumento.id,
        valor=datos.valor,
        codigo_arinc429=palabra.hexadecimal,
        estado_serial="pendiente",
        estado_audio="pendiente",
    )
    db.add(envio)
    db.commit()
    db.refresh(envio)

    mensajes = []
    try:
        envio.estado_serial = SalidaHardware.enviar_serial(palabra)
    except Exception as error:  # El envío persiste para dejar trazabilidad de fallos del dispositivo.
        envio.estado_serial = "error"
        mensajes.append(f"Serial: {error}")
        logger.exception("Error de salida serial para el envío %s", envio.id)
    try:
        envio.estado_audio = SalidaHardware.reproducir_audio(
            datos.valor, instrumento.valor_minimo, instrumento.valor_maximo
        )
    except Exception as error:
        envio.estado_audio = "error"
        mensajes.append(f"Audio: {error}")
        logger.exception("Error de salida de audio para el envío %s", envio.id)

    envio.detalle_salida = "; ".join(mensajes) or None
    db.commit()
    db.refresh(envio)
    db.refresh(instrumento)
    return a_salida(envio)


@app.get("/api/envios", response_model=list[EnvioSalida])
def listar_envios(db: Session = Depends(get_db)):
    envios = db.scalars(
        select(Envio).options(joinedload(Envio.instrumento)).order_by(Envio.id.desc())
    ).all()
    return [a_salida(envio) for envio in envios]


@app.get("/api/envios/{envio_id}", response_model=EnvioSalida)
def obtener_envio(envio_id: int, db: Session = Depends(get_db)):
    envio = db.scalar(
        select(Envio).options(joinedload(Envio.instrumento)).where(Envio.id == envio_id)
    )
    if envio is None:
        raise HTTPException(status_code=404, detail="Envío no encontrado")
    return a_salida(envio)


@app.put("/api/envios/{envio_id}", response_model=EnvioSalida)
def actualizar_envio(envio_id: int, datos: EnvioActualizar, db: Session = Depends(get_db)):
    envio = db.scalar(
        select(Envio).options(joinedload(Envio.instrumento)).where(Envio.id == envio_id)
    )
    instrumento = db.get(Instrumento, datos.instrumento_id)
    if envio is None:
        raise HTTPException(status_code=404, detail="Envío no encontrado")
    if instrumento is None:
        raise HTTPException(status_code=404, detail="Instrumento no encontrado")
    if not instrumento.valor_minimo <= datos.valor <= instrumento.valor_maximo:
        raise HTTPException(status_code=422, detail="El valor está fuera del rango del instrumento")

    try:
        palabra = generar_palabra_bnr(
            etiqueta_octal=instrumento.etiqueta_octal,
            valor=datos.valor,
            escala_lsb=instrumento.escala_lsb,
            sdi=instrumento.sdi,
            ssm=instrumento.ssm,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    envio.instrumento_id = instrumento.id
    envio.valor = datos.valor
    envio.codigo_arinc429 = palabra.hexadecimal
    envio.estado_serial = "no reenviado"
    envio.estado_audio = "no reproducido"
    envio.detalle_salida = "Registro editado; use Crear envío para activar las salidas físicas."
    db.commit()
    db.refresh(envio)
    db.refresh(instrumento)
    return a_salida(envio)


@app.delete("/api/envios/{envio_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_envio(envio_id: int, db: Session = Depends(get_db)):
    envio = db.get(Envio, envio_id)
    if envio is None:
        raise HTTPException(status_code=404, detail="Envío no encontrado")
    db.delete(envio)
    db.commit()
