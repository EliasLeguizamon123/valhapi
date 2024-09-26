from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
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
    printers = [printer for printer in printers if not printer.startswith("Microsoft")]
    printers = [printer for printer in printers if not printer.startswith("Fax")]
    return {"printers": printers}

@router.post("/print")
def print_doc(request: PrintRequest):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    if request.printout == 1:
        pdf_bytes = plain_summary(request)

    temp_file_path = f"{request.test.test_primary.test_id}.pdf"
    with open(temp_file_path, "wb") as f:
        print(f"Writing to file {temp_file_path}")
        f.write(pdf_bytes)

    try:
        printer_name = request.printer_name
        appdata_path = os.getenv('APPDATA')
        pdf_to_printer_path = os.path.join(appdata_path, 'Valhalla', 'PDFToPrinter.exe')

        if not os.path.exists(pdf_to_printer_path):
            raise HTTPException(status_code=404, detail="PDFToPrinter.exe not found in the specified path")

        print(f"Printing in {pdf_to_printer_path}")

        os.system(f"{pdf_to_printer_path} /s {temp_file_path} \"{printer_name}\"")

        return {"detail": "Printed successfully"}

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=str(e))
    
def pounds_to_kg(pounds: float) -> float:
    return round(pounds * 0.453592, 2)

def fat_percentage(segment_fat, total_fat):
    return round((segment_fat / total_fat) * 100, 2)

def plain_summary(request):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    gender = "M" if request.test.test_primary.gender == 1 else "F"

    # Title
    title_data = [
        ["", f"Date: {request.test.test_primary.creation_date.strftime('%Y-%m-%d')}"]
    ]
    title_table = Table(title_data, colWidths=[400, 100])
    title_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))

    story.append(title_table)
    story.append(Paragraph(f"B O D Y  C O M P O S I T I O N  R E P O R T", styles['Title']))
    story.append(Spacer(1, 12))

    # Info general
    info_data = [
        ["Name:", request.test.test_primary.from_field],
        ["Prepared By:", request.test.test_primary.by_field],
        [f"Gender: {gender}", f"Age: {request.test.test_primary.age}"],
        [f"Height: {request.test.test_primary.height} ", f"Weight: {request.test.test_primary.weight} Lbs ({pounds_to_kg(request.test.test_primary.weight)} Kg)"],
        ["Ohms: ", request.test.test_primary.bio_impedance],
        ["Current body weight:", f"{request.test.test_primary.weight} Lbs\n{pounds_to_kg(request.test.test_primary.weight)} Kg"],
        ["Total Body Fat:", f"{request.test.test_primary.body_fat} lbs\n{pounds_to_kg(request.test.test_primary.body_fat)} Kg\n{request.test.test_primary.body_fat_percent} %"],
        ["Visceral Fat:", request.test.test_primary.visceral_fat],
        ["Muscle Mass:", f"{request.test.test_primary.muscle_mass} lbs\n{pounds_to_kg(request.test.test_primary.muscle_mass)} Kg"],
        ["Lean Mass:", f"{request.test.test_primary.lean_mass} lbs\n{pounds_to_kg(request.test.test_primary.lean_mass)} Kg\n{request.test.test_primary.lean_mass_percent} %"],
        ["Body Water:", f"{request.test.test_primary.body_water} lbs\n{request.test.test_primary.body_water_percent} %"],
        ["BMI:", request.test.test_primary.bmi],
    ]
    
    # Create the info table
    info_table = Table(info_data, colWidths=[200, 180])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.white)
    ]))
    story.append(info_table)
    story.append(Spacer(1, 12))

    # Body Fat Displacement
    total_fat = request.test.test_primary.body_fat
    segmental_data = [
        ["Body Fat Displacement", "", "", "" ],
        ["Torso", f"{request.test.test_segmental.torso} Lbs", f"{pounds_to_kg(request.test.test_segmental.torso)} Kg", f"{fat_percentage(request.test.test_segmental.torso, total_fat)} %"],
        ["Right Arm", f"{request.test.test_segmental.right_arm} Lbs", f"{pounds_to_kg(request.test.test_segmental.right_arm)} Kg", f"{fat_percentage(request.test.test_segmental.right_arm, total_fat)} %"],
        ["Left Arm", f"{request.test.test_segmental.left_arm} Lbs", f"{pounds_to_kg(request.test.test_segmental.left_arm)} Kg", f"{fat_percentage(request.test.test_segmental.left_arm, total_fat)} %"],
        ["Right Leg", f"{request.test.test_segmental.right_leg} Lbs", f"{pounds_to_kg(request.test.test_segmental.right_leg)} Kg", f"{fat_percentage(request.test.test_segmental.right_leg, total_fat)} %"],
        ["Left Leg", f"{request.test.test_segmental.left_leg} Lbs", f"{pounds_to_kg(request.test.test_segmental.left_leg)} Kg", f"{fat_percentage(request.test.test_segmental.left_leg, total_fat)} %"],
    ]

    segmental_table = Table(segmental_data, colWidths=[200, 60, 60, 60])
    segmental_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('GRID', (0, 0), (-1, -1), 1, colors.white)
    ]))
    story.append(segmental_table)
    story.append(Spacer(1, 12))

    # Basal Metabolic Rate
    bmr_data = [
        ["Activity Level", "Daily Caloric Needs"],
        ["Basal Metabolic Rate:", f"{request.test.test_energy.basal_metabolic_rate} Calories/Day"],
        ["Very light activity:", f"{request.test.test_energy.very_light_activity} Calories/Day"],
        ["Light activity:", f"{request.test.test_energy.light_activity} Calories/Day"],
        ["Moderate activity:", f"{request.test.test_energy.moderate_activity} Calories/Day"],
        ["Heavy activity:", f"{request.test.test_energy.heavy_activity} Calories/Day"],
        ["Very heavy activity:", f"{request.test.test_energy.very_heavy_activity} Calories/Day"]
    ]

    bmr_table = Table(bmr_data, colWidths=[200, 180])
    bmr_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.white)
    ]))
    story.append(bmr_table)
    
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    
    return pdf_bytes