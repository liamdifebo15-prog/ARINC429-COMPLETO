# Administrador de envíos ARINC 429

Aplicación web en español para seleccionar instrumentos, cargar un valor y registrar un envío. Incluye API REST, CRUD persistente con MySQL, codificación de palabra ARINC 429 BNR de 32 bits y adaptadores de salida serial/audio que permanecen simulados por seguridad.

## Requisitos

- Python 3.12 (3.10+ compatible)
- Docker Compose para iniciar MySQL, o una instancia MySQL 8 accesible
- Para pruebas de audio habilitadas: dispositivo ALSA y dependencias del sistema de `sounddevice`

## Inicio

1. Copiar `.env.example` a `.env` y ajustar `DATABASE_URL` para la base de datos local.
2. Iniciar MySQL con Docker (`docker compose up -d mysql`) o configurar el MySQL instalado en el equipo, como se indica abajo.
3. Crear y activar un entorno virtual, luego instalar `requirements.txt`.
4. Desde la raíz del proyecto iniciar: `uvicorn app.main:app --reload`.
5. Abrir `http://127.0.0.1:8000`. La documentación interactiva de la API está en `/docs`.

### MySQL instalado localmente (sin Docker)

En Ubuntu, si el comando `mysql -u root` responde `Access denied`, usa `sudo mysql` para entrar como administrador del servicio. Ejecuta estas sentencias SQL y reemplaza `CAMBIA_ESTA_CLAVE` por una clave local segura compuesta por letras y números:

```sql
CREATE DATABASE IF NOT EXISTS arinc429 CHARACTER SET utf8mb4;
CREATE USER IF NOT EXISTS 'arinc_user'@'localhost' IDENTIFIED BY 'CAMBIA_ESTA_CLAVE';
CREATE USER IF NOT EXISTS 'arinc_user'@'127.0.0.1' IDENTIFIED BY 'CAMBIA_ESTA_CLAVE';
ALTER USER 'arinc_user'@'localhost' IDENTIFIED BY 'CAMBIA_ESTA_CLAVE';
ALTER USER 'arinc_user'@'127.0.0.1' IDENTIFIED BY 'CAMBIA_ESTA_CLAVE';
GRANT ALL PRIVILEGES ON arinc429.* TO 'arinc_user'@'localhost';
GRANT ALL PRIVILEGES ON arinc429.* TO 'arinc_user'@'127.0.0.1';
```

Luego, en `.env`, configura `DATABASE_URL=mysql+pymysql://arinc_user:CAMBIA_ESTA_CLAVE@127.0.0.1:3306/arinc429` usando exactamente la misma clave. Si la clave contiene símbolos reservados en una URL, codifícala o elige letras y números para desarrollo local.

Al iniciar se crean las tablas `instrumentos` y `envios`. Si no hay instrumentos, se cargan ejemplos iniciales. La API permite listar instrumentos y crear, listar, consultar, editar y eliminar envíos. Endpoints CRUD: `POST /api/envios`, `GET /api/envios`, `GET /api/envios/{id}`, `PUT /api/envios/{id}`, `DELETE /api/envios/{id}`.

## ARINC 429 y hardware: importante

La codificación implementada es un **ejemplo BNR** en signo-magnitud, con etiqueta octal, SDI, SSM y paridad impar. La asignación de escala/LSB, formato BNR, signo, etiqueta y SSM debe cotejarse con el ICD del instrumento; no se puede asumir que esos valores de ejemplo sean válidos para un sistema real.

La escritura de cuatro bytes a un puerto serial UART **no produce por sí sola una señal ARINC 429**. Para una prueba física hace falta una interfaz/transmisor ARINC 429 que genere el nivel diferencial, velocidad y temporización correctos. Un UART USB básico no debe conectarse directamente a un bus de aviónica.

La salida de audio genera un tono de 440 Hz cuya amplitud digital escala con el valor del envío. Eso no garantiza una tensión analógica calibrada en el jack: la tensión real depende del DAC, control de volumen, carga y amplificador. No conectar auriculares o instrumentación a circuitos desconocidos. Calibrar con equipo de medición y usar aislamiento/limitación adecuados; el audio se mantiene deshabilitado por defecto.

Para habilitar adaptadores solo en banco aislado, ajustar las variables `ARINC429_OUTPUT_ENABLED=true` y `AUDIO_OUTPUT_ENABLED=true` después de configurar la interfaz correcta. La aplicación no es un equipo certificado ni apto para conectarse a una aeronave.

## Validación

Ejecutar `pytest`. Las pruebas cubren tamaño de palabra, paridad impar, validación de etiqueta y escala.
