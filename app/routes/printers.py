from fastapi import APIRouter
import win32print # type: ignore

router = APIRouter()

@router.get("/")
def get_printers():
    printers = [printer[2] for printer in win32print.EnumPrinters(2)]
    
    # Exclude all the virtual printers
    printers = [printer for printer in printers if not printer.startswith("Microsoft XPS")]
    printers = [printer for printer in printers if not printer.startswith("OneNote")]
    printers = [printer for printer in printers if not printer.startswith("Fax")]
    return {"printers": printers}