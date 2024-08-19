from fastapi import APIRouter
import win32print # type: ignore

router = APIRouter()

@router.get("/")
def get_printers():
    printers = [printer[2] for printer in win32print.EnumPrinters(2)]
    return {"printers": printers}