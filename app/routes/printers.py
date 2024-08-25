from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from io import BytesIO
from fpdf import FPDF
import win32print, os
from pathlib import Path

from sql_data.schemas.tests_primary import TestResponse

router = APIRouter()

class PrintRequest(BaseModel):
    printout: int
    printer_name: str
    test: TestResponse

@router.get("/")
def get_printers():
    printers = [printer[2] for printer in win32print.EnumPrinters(2)]
    
    # Exclude all the virtual printers
    printers = [printer for printer in printers if not printer.startswith("Microsoft XPS")]
    printers = [printer for printer in printers if not printer.startswith("OneNote")]
    printers = [printer for printer in printers if not printer.startswith("Fax")]
    return {"printers": printers}

@router.post("/print")
def print_doc(request: PrintRequest):
    # Crear el contenido de texto plano
    text_content = ""

    if request.printout == 1:
        text_content += "BODY COMPOSITION REPORT\n"
        text_content += f"Name: {request.test.test_primary.by_field}\n"
        text_content += f"Weight: {request.test.test_primary.weight}\n"
        text_content += f"BMI: {request.test.test_primary.bmi}\n"
        # Agrega más campos aquí como lo necesites

    # Obtener la ruta de la carpeta "Documents"
    documents_path = Path.home() / "Documents"
    
    # Ruta del archivo a guardar
    file_path = documents_path / "body_composition_report.txt"

    try:
        # Guardar el contenido en un archivo .txt
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(text_content)

        return {"detail": f"File saved successfully at {file_path}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    # try:
    #     # Abrir la impresora
    #     printer_handle = win32print.OpenPrinter(request.printer_name)
    #     doc_info = ("Body composition report", None, "RAW")
    #     win32print.StartDocPrinter(printer_handle, 1, doc_info)
    #     win32print.StartPagePrinter(printer_handle)

    #     # Enviar el texto a la impresora
    #     win32print.WritePrinter(printer_handle, text_content.encode('utf-8'))

    #     win32print.EndPagePrinter(printer_handle)
    #     win32print.EndDocPrinter(printer_handle)
    #     win32print.ClosePrinter(printer_handle)

    #     return {"detail": "Printed successfully"}

    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))