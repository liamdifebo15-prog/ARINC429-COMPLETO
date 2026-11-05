# Instrucciones del proyecto

- Aplicación Python con FastAPI, SQLAlchemy y MySQL para administrar envíos de instrumentos.
- Mantener toda salida física deshabilitada por defecto; solo habilitarla para pruebas controladas de laboratorio.
- El formato BNR, etiquetas, bits SDI/SSM, unidades y escala son configurables/ejemplos: validar siempre con ICD/documentación del equipo real.
- Un puerto UART convencional no genera señalización física ARINC 429; requiere un transmisor/adaptador ARINC 429 compatible.
- La amplitud de audio de la salida depende de la tarjeta de sonido, DAC y amplificador; no asumir tensión calibrada sin medición y calibración de hardware.
- No conectar auriculares ni circuitos de aviónica directamente a interfaces no aisladas o no certificadas.
- Ejecutar `pytest` para validar la codificación ARINC.
