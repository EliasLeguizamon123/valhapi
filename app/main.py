from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from logging.config import dictConfig
import os, uvicorn
from sqlalchemy import text, inspect
from sqlalchemy.exc import ProgrammingError, OperationalError

from dump import initialize_data
from sql_data.config import engine, Base
from alembic import command
from alembic.config import Config

from app.routes import members, core_software, operator_settings, tests, printers, scales

app = FastAPI()

app.include_router(members.router, prefix="/members")
app.include_router(core_software.router, prefix="/core_software")
app.include_router(operator_settings.router, prefix="/operator_settings")
app.include_router(tests.router, prefix="/tests")
app.include_router(printers.router, prefix="/printers")
app.include_router(scales.router, prefix="/scales")


origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def is_database_up_to_date(engine) -> bool:
    alembic_cfg = Config("alembic.ini")

    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version_num FROM alembic_version"))
            db_version = result.scalar()
    except (ProgrammingError, OperationalError):
        print("La tabla alembic_version no existe, aplicando todas las migraciones.")
        return False

    script = command.ScriptDirectory.from_config(alembic_cfg)
    latest_version = script.get_current_head()

    return db_version == latest_version

def run_migrations(engine):
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.attributes['engine'] = engine

    if not is_database_up_to_date(engine):
        command.upgrade(alembic_cfg, "head")
    else:
        print("Base de datos ya está actualizada. No es necesario ejecutar migraciones.")

@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    initialize_data()

@app.get("/ping")
def get_current_time():
    current_time = datetime.now().isoformat()
    return current_time

DEFAULT_PORT = 8000

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