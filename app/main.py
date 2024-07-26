from fastapi import FastAPI
from datetime import datetime
from logging.config import dictConfig
import os, uvicorn

from dump import initialize_data

from app.routes import members, core_software

app = FastAPI()

app.include_router(members.router, prefix="/members")
app.include_router(core_software.router, prefix="/core_software")

@app.on_event("startup")
def startup_event():
    initialize_data()

@app.get("/ping")
def get_current_time():
    current_time = datetime.now().isoformat()
    return current_time


# Run with pyinstaller
DEFAULT_PORT = 12358

# Configurar el logger para escribir en un archivo
log_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'valhapi.log')

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "fmt": "%(levelprefix)s %(asctime)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "use_colors": None
        },
        "access": {
            "fmt": '%(levelprefix)s %(asctime)s - %(client_addr)s - "%(request_line)s" %(status_code)s',
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.FileHandler",
            "filename": log_filename,
            "mode": "a",
        },
        "access": {
            "formatter": "access",
            "class": "logging.FileHandler",
            "filename": log_filename,
            "mode": "a",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": "INFO",
        },
        "uvicorn.error": {
            "level": "INFO",
        },
        "uvicorn.access": {
            "handlers": ["access"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

dictConfig(log_config)

if __name__ == "__main__":
    port = int(os.getenv("PORT", DEFAULT_PORT))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_config=log_config)