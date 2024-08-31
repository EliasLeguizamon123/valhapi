from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import win32print, io, os # type: ignore

from sql_data.schemas.tests_primary import TestResponse

router = APIRouter()

class PrintRequest(BaseModel):
    printout: int
    printer_name: str
    test: TestResponse

@router.get("/")
def get_printers():
    printers = [printer[2] for printer in win32print.EnumPrinters(2)]
    
    printers = [printer for printer in printers if not printer.startswith("Microsoft XPS")]
    printers = [printer for printer in printers if not printer.startswith("OneNote")]
    # printers = [printer for printer in printers if not printer.startswith("Microsoft")]
    printers = [printer for printer in printers if not printer.startswith("Fax")]
    return {"printers": printers}

@router.post("/print")
def print_doc(request: PrintRequest):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    if request.printout == 1:
        story.append(Paragraph("BODY COMPOSITION REPORT", styles['Title']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Name: {request.test.test_primary.by_field}", styles['Normal']))
        story.append(Paragraph(f"Test by: {request.test.test_primary.from_field}", styles['Normal']))
        story.append(Paragraph(f"Weight: {request.test.test_primary.weight}", styles['Normal']))
        story.append(Paragraph(f"BMI: {request.test.test_primary.bmi}", styles['Normal']))
        story.append(Paragraph(f"Body fat: {request.test.test_primary.body_fat}", styles['Normal']))
        story.append(Paragraph(f"Bio impedance: {request.test.test_primary.bio_impedance}", styles['Normal']))
        story.append(Paragraph(f"Visceral fat: {request.test.test_primary.visceral_fat}", styles['Normal']))
        story.append(Paragraph(f"Lean mass: {request.test.test_primary.lean_mass}", styles['Normal']))
        story.append(Paragraph(f"Muscle mass: {request.test.test_primary.muscle_mass}", styles['Normal']))
        story.append(Paragraph(f"Body water: {request.test.test_primary.body_water}", styles['Normal']))
        story.append(Paragraph(f"Creation date: {request.test.test_primary.creation_date}", styles['Normal']))
        story.append(Paragraph(f"Basal metabolic rate: {request.test.test_energy.basal_metabolic_rate}", styles['Normal']))
        story.append(Paragraph(f"Very light activity: {request.test.test_energy.very_light_activity}", styles['Normal']))
        story.append(Paragraph(f"Light activity: {request.test.test_energy.light_activity}", styles['Normal']))
        story.append(Paragraph(f"Moderate activity: {request.test.test_energy.moderate_activity}", styles['Normal']))
        story.append(Paragraph(f"Heavy activity: {request.test.test_energy.heavy_activity}", styles['Normal']))
        story.append(Paragraph(f"Very heavy activity: {request.test.test_energy.very_heavy_activity}", styles['Normal']))
        story.append(Paragraph(f"Torso: {request.test.test_segmental.torso}", styles['Normal']))
        story.append(Paragraph(f"Right arm: {request.test.test_segmental.right_arm}", styles['Normal']))
        story.append(Paragraph(f"Left arm: {request.test.test_segmental.left_arm}", styles['Normal']))
        story.append(Paragraph(f"Right leg: {request.test.test_segmental.right_leg}", styles['Normal']))
        story.append(Paragraph(f"Left leg: {request.test.test_segmental.left_leg}", styles['Normal']))
    
    doc.build(story)
    pdf_bytes = buffer.getvalue()

    temp_file_path = "temp_report.pdf"
    with open(temp_file_path, "wb") as f:
        print(f"Writing to file {temp_file_path}")
        f.write(pdf_bytes)

    try:
        printer_name = request.printer_name
        appdata_path = os.getenv('APPDATA')
        pdf_to_printer_path = os.path.join(appdata_path, 'Valhalla', 'PDFToPrinter.exe')
        
        os.system(f"{pdf_to_printer_path} {temp_file_path} \"{printer_name}\"")

        return {"detail": "Printed successfully"}

    except Exception as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=str(e))