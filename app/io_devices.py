import math
import os

import numpy as np

from app.arinc429 import PalabraArinc429


class SalidaHardware:
    """Salidas desactivadas por defecto; habilitarlas solo en banco de pruebas."""

    @staticmethod
    def enviar_serial(palabra: PalabraArinc429) -> str:
        if os.getenv("ARINC429_OUTPUT_ENABLED", "false").lower() != "true":
            return "simulado"

        puerto = os.getenv("ARINC429_SERIAL_PORT")
        if not puerto:
            raise RuntimeError("Falta configurar ARINC429_SERIAL_PORT")

        import serial

        velocidad = int(os.getenv("ARINC429_SERIAL_BAUD", "115200"))
        with serial.Serial(puerto, baudrate=velocidad, timeout=1, write_timeout=1) as enlace:
            escritos = enlace.write(palabra.bytes_serial)
            enlace.flush()
        if escritos != 4:
            raise RuntimeError(f"Se enviaron {escritos} de los 4 bytes ARINC")
        return "enviado"

    @staticmethod
    def reproducir_audio(valor: float, minimo: float, maximo: float) -> str:
        if os.getenv("AUDIO_OUTPUT_ENABLED", "false").lower() != "true":
            return "simulado"
        if maximo <= minimo:
            raise ValueError("El rango del instrumento no es válido")

        import sounddevice as sd

        frecuencia_muestreo = int(os.getenv("AUDIO_SAMPLE_RATE", "44100"))
        duracion = float(os.getenv("AUDIO_DURATION_SECONDS", "0.25"))
        amplitud_maxima = float(os.getenv("AUDIO_MAX_AMPLITUDE", "0.2"))
        if not 0 < amplitud_maxima <= 1:
            raise ValueError("AUDIO_MAX_AMPLITUDE debe estar entre 0 y 1")

        proporcion = min(1.0, max(0.0, (valor - minimo) / (maximo - minimo)))
        amplitud = proporcion * amplitud_maxima
        muestras = max(1, int(frecuencia_muestreo * duracion))
        tiempo = np.arange(muestras) / frecuencia_muestreo
        tono = (amplitud * np.sin(2 * math.pi * 440 * tiempo)).astype(np.float32)
        sd.play(tono, samplerate=frecuencia_muestreo, blocking=True)
        return "reproducido"
