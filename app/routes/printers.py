from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import cm
import win32print, io, os # type: ignore
from typing import Optional
from fpdf import FPDF
from pypdf import PdfWriter

from sql_data.config import SessionLocal
from sql_data.schemas.tests_primary import TestResponse
from sql_data.schemas.operator_settings import OperatorSettings, OperatorSettingsCreate
from sql_data.models.operator_settings import OperatorSettings as OperatorSettingsModel

router = APIRouter()

class Includes(BaseModel):
    body_fat: bool
    weight: bool
    bio_impedance: bool
    visceral_fat: bool
    muscle_mass: bool
    lean_mass: bool
    body_water: bool
    bmi: bool
    activity_section: bool
    basal_metabolic_rate: bool
    segmental_section: bool

class PrintRequest(BaseModel):
    printout: int
    printer_name: str
    test: TestResponse
    includes: Optional[Includes] = None
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def get_printers():
    printers = [printer[2] for printer in win32print.EnumPrinters(2)]
    
    printers = [printer for printer in printers if not printer.startswith("Microsoft XPS")]
    printers = [printer for printer in printers if not printer.startswith("OneNote")]
    printers = [printer for printer in printers if not printer.startswith("Microsoft")]
    printers = [printer for printer in printers if not printer.startswith("Fax")]
    return {"printers": printers}

@router.post("/print")
def print_doc(request: PrintRequest, db: Session = Depends(get_db)):
    operator_settings = db.query(OperatorSettingsModel).first()
    
    from_field_value = request.test.test_primary.from_field
    if ' ' in from_field_value:
        from_field_value = from_field_value.split()[0]
    
    if request.printout == 1:
        pdf_bytes = plain_summary(request, operator_settings.company_name)
        if not isinstance(pdf_bytes, bytes):
            raise Exception("Error generating PDF: output is not bytes")
        temp_file_path = f"plainSummary_{from_field_value}_{request.test.test_primary.creation_date.strftime('%Y-%m-%d')}.pdf"
    elif request.printout == 2 or request.printout == 3:
        pdf_bytes = combine_pdf(p055b(request, operator_settings.company_name), plain_summary(request, operator_settings.company_name))
        if not isinstance(pdf_bytes, bytes):
            raise Exception("Error generating PDF: output is not bytes")
        temp_file_path = f"p055b_{from_field_value}_{request.test.test_primary.creation_date.strftime('%Y-%m-%d')}.pdf"
    elif request.printout == 4:
        pdf_bytes = p111a(request)
        if not isinstance(pdf_bytes, bytes):
            raise Exception("Error generating PDF: output is not bytes")
        temp_file_path = f"p111a_{from_field_value}_{request.test.test_primary.creation_date.strftime('%Y-%m-%d')}.pdf"
    elif request.printout == 5:
        pdf_bytes = p511a(request)
        if not isinstance(pdf_bytes, bytes):
            raise Exception("Error generating PDF: output is not bytes")
        temp_file_path = f"p511a_{from_field_value}_{request.test.test_primary.creation_date.strftime('%Y-%m-%d')}.pdf"
    elif request.printout == 6 and request.includes:
        pdf_bytes = custom_summary(request, operator_settings.company_name)
        if not isinstance(pdf_bytes, bytes):
            raise Exception("Error generating PDF: output is not bytes")
        temp_file_path = f"customSummary_{from_field_value}_{request.test.test_primary.creation_date.strftime('%Y-%m-%d')}.pdf"
    else: 
        temp_file_path = f"plainSummary_{from_field_value}_{request.test.test_primary.creation_date.strftime('%Y-%m-%d')}.pdf"

    with open(temp_file_path, "wb") as f:
        print(f"Writing to file {temp_file_path}")
        f.write(pdf_bytes)

    try:
        printer_name = request.printer_name
        appdata_path = os.getenv('APPDATA')
        reverse = True if operator_settings.collation == 'Top Load' else False
        pdf_to_printer_path = os.path.join(appdata_path, 'Valhalla', 'PDFToPrinter.exe')
        print(f"PDFToPrinter.exe path: {pdf_to_printer_path}, {reverse}")

        if not os.path.exists(pdf_to_printer_path):
            raise HTTPException(status_code=404, detail="PDFToPrinter.exe not found in the specified path")

        print(f"Printing in {pdf_to_printer_path}")
        
        page_range = "z-1" if reverse else ""
        
        command = f"{pdf_to_printer_path} /s {temp_file_path} \"{printer_name}\""
        
        print (f"command: {command}")
        if page_range:
            command += f" pages={page_range}"
        
        result = os.system(command)

        # result = os.system(f"{pdf_to_printer_path} /s {temp_file_path} \"{printer_name}\"")
        if result != 0:
            raise Exception(f"Error executing print command, result code: {result}")

        return {"detail": "Printed successfully"}

    except HTTPException as http_exc:
        return http_exc
    except Exception as e:
        print(f"Error: {e}")
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        return HTTPException(status_code=500, detail=str(e))
    
def pounds_to_kg(pounds: float) -> float:
    return round(pounds * 0.453592, 2)

def plain_summary(request, company_name=""):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    gender = "M" if request.test.test_primary.gender == 0 else "F"
    parts = request.test.test_primary.height.split(" ")
    formatted_height = f"{parts[0]} {parts[1]}\n{parts[2][:-2]} cm"
    
    styles.add(ParagraphStyle(
        name='CompanyName',
        fontName='Helvetica-Bold',
        fontSize=12,               
        textColor=colors.black,    
        alignment=1,               
        spaceAfter=12              
    ))
    
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

    story.append(Spacer(1, -1 * cm))
    story.append(title_table)
    story.append(Paragraph(f"BODY COMPOSITION REPORT", styles['Title']))
    story.append(Paragraph(f"{company_name}", styles['CompanyName']))
    story.append(Spacer(1, 12))

    # Info general
    info_data = [
        [f"Name: {request.test.test_primary.from_field}", f"Prepared By: {request.test.test_primary.by_field}"],
        [f"Gender: {gender}", f"Age: {request.test.test_primary.age}"],
        [f"Height: ", f"{formatted_height}"],
        ["Current body weight:", f"{round(request.test.test_primary.weight, 1)} Lbs\n{round(pounds_to_kg(request.test.test_primary.weight), 1)} Kg"],
        ["Total Body Fat:", f"{round(request.test.test_primary.body_fat, 1)} lbs\n{round(pounds_to_kg(request.test.test_primary.body_fat), 1)} Kg\n{round(request.test.test_primary.body_fat_percent, 1)} %"],
        ["Visceral Fat:", int(request.test.test_primary.visceral_fat)],
        ["Muscle Mass:", f"{round(request.test.test_primary.muscle_mass, 1)} lbs\n{round(pounds_to_kg(request.test.test_primary.muscle_mass), 1)} Kg"],
        ["Fat Free Mass:", f"{round(request.test.test_primary.lean_mass, 1)} lbs\n{round(pounds_to_kg(request.test.test_primary.lean_mass), 1)} Kg\n{round(request.test.test_primary.lean_mass_percent, 1)} %"],
        ["Total body Water:", f"{round(request.test.test_primary.body_water, 1)} lbs\n{round(pounds_to_kg(request.test.test_primary.body_water), 1)} Kg\n{round(request.test.test_primary.body_water_percent, 1)} %"],
        ["BMI:", round(request.test.test_primary.bmi, 1)],
        ["Ohms: ", int(request.test.test_primary.bio_impedance)],
    ]
    
    # Create the info table
    info_table = Table(info_data, colWidths=[200, 180])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('ALIGN', (1, 2), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.white),
        ('LINEBELOW', (0, 2), (-1, 2), 1, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black)
    ]))
    story.append(info_table)
    story.append(Spacer(1, 12))

    # Body Fat Displacement
    segmental_data = [
        ["Body Fat Displacement", "", "", ""],
        ["Torso", f"{round(request.test.test_segmental.torso, 1)} Lbs", f"{round(pounds_to_kg(request.test.test_segmental.torso), 1)} Kg", f"{round(request.test.test_segmental.torso_percent, 1)} %"],
        ["Right Arm", f"{round(request.test.test_segmental.right_arm, 1)} Lbs", f"{round(pounds_to_kg(request.test.test_segmental.right_arm), 1)} Kg", f"{round(request.test.test_segmental.right_arm_percent, 1)} %"],
        ["Left Arm", f"{round(request.test.test_segmental.left_arm, 1)} Lbs", f"{round(pounds_to_kg(request.test.test_segmental.left_arm), 1)} Kg", f"{round(request.test.test_segmental.left_arm_percent, 1)} %"],
        ["Right Leg", f"{round(request.test.test_segmental.right_leg, 1)} Lbs", f"{round(pounds_to_kg(request.test.test_segmental.right_leg), 1)} Kg", f"{round(request.test.test_segmental.right_leg_percent, 1)} %"],
        ["Left Leg", f"{round(request.test.test_segmental.left_leg, 1)} Lbs", f"{round(pounds_to_kg(request.test.test_segmental.left_leg), 1)} Kg", f"{round(request.test.test_segmental.left_leg_percent, 1)} %"],
    ]

    segmental_table = Table(segmental_data, colWidths=[200, 60, 60, 60])
    segmental_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('GRID', (0, 0), (-1, -1), 1, colors.white),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black)
    ]))
    story.append(segmental_table)
    story.append(Spacer(1, 12))
    
    basal_data = [
        ["Basal Metabolic Rate:", f"{int(request.test.test_energy.basal_metabolic_rate)} Calories/Day"],
    ]

    basal_table = Table(basal_data, colWidths=[200, 180])
    
    basal_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.white)
    ]))
    story.append(basal_table)
    story.append(Spacer(1, 12))
    
    # Basal Metabolic Rate
    bmr_data = [
        ["Activity Level", "Daily Caloric Needs"],
        ["Very light activity:", f"{int(request.test.test_energy.very_light_activity)} Calories/Day"],
        ["Light activity:", f"{int(request.test.test_energy.light_activity)} Calories/Day"],
        ["Moderate activity:", f"{int(request.test.test_energy.moderate_activity)} Calories/Day"],
        ["Heavy activity:", f"{int(request.test.test_energy.heavy_activity)} Calories/Day"],
        ["Very heavy activity:", f"{int(request.test.test_energy.very_heavy_activity)} Calories/Day"]
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

def custom_summary(request, company_name=""):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    gender = "M" if request.test.test_primary.gender == 0 else "F"
    parts = request.test.test_primary.height.split(" ")
    formatted_height = f"{parts[0]} {parts[1]}\n{parts[2][:-2]} cm"
    
    styles.add(ParagraphStyle(
        name='CompanyName',
        fontName='Helvetica-Bold',
        fontSize=12,               
        textColor=colors.black,    
        alignment=1,               
        spaceAfter=12              
    ))

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

    story.append(Spacer(1, -1 * cm))
    story.append(title_table)
    story.append(Paragraph("BODY COMPOSITION REPORT", styles['Title']))
    story.append(Paragraph(f"{company_name}", styles['CompanyName']))
    story.append(Spacer(1, 12))

    # General Info
    info_data = [
        [f"Name: {request.test.test_primary.from_field}", f"Prepared By: {request.test.test_primary.by_field}"],
        [f"Gender: {gender}", f"Age: {request.test.test_primary.age}"],
        [f"Height: ", f"{formatted_height}"],
    ]
    
    if request.includes.weight:
        info_data.append(["Current body weight:", f"{round(request.test.test_primary.weight, 1)} Lbs\n{round(pounds_to_kg(request.test.test_primary.weight), 1)} Kg"])
    if request.includes.body_fat:
        info_data.append(["Total Body Fat:", f"{round(request.test.test_primary.body_fat, 1)} lbs\n{round(pounds_to_kg(request.test.test_primary.body_fat), 1)} Kg\n{round(request.test.test_primary.body_fat_percent, 1)} %"])
    if request.includes.visceral_fat:
        info_data.append(["Visceral Fat:", int(request.test.test_primary.visceral_fat)])
    if request.includes.muscle_mass:
        info_data.append(["Muscle Mass:", f"{round(request.test.test_primary.muscle_mass, 1)} lbs\n{round(pounds_to_kg(request.test.test_primary.muscle_mass), 1)} Kg"])
    if request.includes.lean_mass:
        info_data.append(["Fat Free Mass:", f"{round(request.test.test_primary.lean_mass, 1)} lbs\n{round(pounds_to_kg(request.test.test_primary.lean_mass), 1)} Kg\n{round(request.test.test_primary.lean_mass_percent, 1)} %"])
    if request.includes.body_water:
        info_data.append(["Total body Water:", f"{round(request.test.test_primary.body_water, 1)} lbs\n{round(pounds_to_kg(request.test.test_primary.body_water), 1)} Kg\n{round(request.test.test_primary.body_water_percent, 1)} %"])
    if request.includes.bmi:
        info_data.append(["BMI:", round(request.test.test_primary.bmi, 1)])
    if request.includes.bio_impedance:
        info_data.append(["Ohms: ", round(request.test.test_primary.bio_impedance, 1)])
    
    # Create the info table
    info_table = Table(info_data, colWidths=[200, 180])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('ALIGN', (1, 2), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.white),
        ('LINEBELOW', (0, 2), (-1, 2), 1, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black)  
    ]))
    story.append(info_table)
    story.append(Spacer(1, 12))

    # Body Fat Displacement
    if request.includes and request.includes.segmental_section:
        total_fat = request.test.test_primary.body_fat
        segmental_data = [
            ["Body Fat Displacement", "", "", ""],
            ["Torso", f"{round(request.test.test_segmental.torso, 1)} Lbs", f"{round(pounds_to_kg(request.test.test_segmental.torso), 1)} Kg", f"{round(request.test.test_segmental.torso_percent, 1)} %"],
            ["Right Arm", f"{round(request.test.test_segmental.right_arm, 1)} Lbs", f"{round(pounds_to_kg(request.test.test_segmental.right_arm), 1)} Kg", f"{round(request.test.test_segmental.right_arm_percent, 1)} %"],
            ["Left Arm", f"{round(request.test.test_segmental.left_arm, 1)} Lbs", f"{round(pounds_to_kg(request.test.test_segmental.left_arm), 1)} Kg", f"{round(request.test.test_segmental.left_arm_percent, 1)} %"],
            ["Right Leg", f"{round(request.test.test_segmental.right_leg, 1)} Lbs", f"{round(pounds_to_kg(request.test.test_segmental.right_leg), 1)} Kg", f"{round(request.test.test_segmental.right_leg_percent, 1)} %"],
            ["Left Leg", f"{round(request.test.test_segmental.left_leg, 1)} Lbs", f"{round(pounds_to_kg(request.test.test_segmental.left_leg), 1)} Kg", f"{round(request.test.test_segmental.left_leg_percent, 1)} %"],
        ]

        segmental_table = Table(segmental_data, colWidths=[200, 60, 60, 60])
        segmental_table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.white),
            ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black)
        ]))
        story.append(segmental_table)
        story.append(Spacer(1, 12))
        
        # Basal Metabolic Rate
        if request.includes.basal_metabolic_rate:
            basal_data = [
                ["Basal Metabolic Rate:", f"{int(request.test.test_energy.basal_metabolic_rate)} Calories/Day"],
            ]

            basal_table = Table(basal_data, colWidths=[200, 180])
            basal_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.white)
            ]))
            story.append(basal_table)
            story.append(Spacer(1, 12))


    # Activity Section
    if request.includes and request.includes.activity_section:
        bmr_data = [
            ["Activity Level", "Daily Caloric Needs"],
            ["Very light activity:", f"{int(request.test.test_energy.very_light_activity)} Calories/Day"],
            ["Light activity:", f"{int(request.test.test_energy.light_activity)} Calories/Day"],
            ["Moderate activity:", f"{int(request.test.test_energy.moderate_activity)} Calories/Day"],
            ["Heavy activity:", f"{int(request.test.test_energy.heavy_activity)} Calories/Day"],
            ["Very heavy activity:", f"{int(request.test.test_energy.very_heavy_activity)} Calories/Day"]
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

    # Build the PDF document
    doc.build(story)
    pdf_bytes = buffer.getvalue()

    return pdf_bytes

def p111a(request):
    gender = "M" if request.test.test_primary.gender == 0 else "F"
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", size=10)

    pdf.set_text_color(0, 0, 0)  # Black in RGB
    
    pdf.set_xy(30, 20)
    pdf.cell(40, 10, f"{request.test.test_primary.from_field}")
    
    pdf.set_xy(30, 36)
    pdf.cell(40, 10, f"{request.test.test_primary.creation_date.strftime('%Y/%m/%d')}")
    
    pdf.set_xy(23, 50)
    pdf.cell(40, 10, f"{gender}")
    
    pdf.set_xy(37, 50)
    pdf.cell(40, 10, f"{request.test.test_primary.age}")
    
    pdf.set_xy(50, 50)
    pdf.cell(40, 10, f"{request.test.test_primary.height}")
    
    pdf.set_xy(23, 55)
    pdf.cell(40, 10, f"Ohms: {int(request.test.test_primary.bio_impedance)}")
    
    pdf.set_xy(105, 40)
    pdf.multi_cell(0, 7, f"{round(request.test.test_primary.weight, 1)} Lbs\n{round(pounds_to_kg(request.test.test_primary.weight), 1)} Kg")
    
    pdf.set_xy(105, 72)
    pdf.multi_cell(0, 5, f"{round(request.test.test_primary.body_fat, 1)} Lbs\n{round(pounds_to_kg(request.test.test_primary.body_fat), 1)} Kg\n{round(request.test.test_primary.body_fat_percent, 1)} %")

    pdf.set_xy(105, 130)
    pdf.cell(40, 10, f"{int(request.test.test_primary.visceral_fat)}")

    pdf.set_xy(145, 42)
    pdf.cell(40, 10, f"{round(request.test.test_primary.bmi, 1)}")
    
    pdf.set_xy(145, 72)
    pdf.multi_cell(0, 7, f"{round(request.test.test_primary.muscle_mass, 1)} Lbs\n{round(pounds_to_kg(request.test.test_primary.muscle_mass), 1)} Kg")
    
    pdf.set_xy(180, 72)
    pdf.multi_cell(0, 5, f"{round(request.test.test_primary.body_water, 1)} Lbs\n{round(pounds_to_kg(request.test.test_primary.body_water), 1)} Kg\n{round(request.test.test_primary.body_water_percent, 1)} %")
    
    # Torso
    pdf.set_xy(135, 130)  # Parte izquierda (título)
    pdf.cell(40, 5, "Torso: ", align='L')

    pdf.set_xy(155, 130)  # Parte derecha (Lbs, Kg, y %)
    pdf.cell(0, 5, f"{round(request.test.test_segmental.torso, 1)} Lbs  {round(pounds_to_kg(request.test.test_segmental.torso), 1)} Kg  {round(request.test.test_segmental.torso_percent, 1)} %")

    # Left Leg
    pdf.set_xy(135, 135)  # Parte izquierda (título)
    pdf.cell(40, 5, "Left Leg: ", align='L')

    pdf.set_xy(155, 135)  # Parte derecha (Lbs, Kg, y %)
    pdf.cell(0, 5, f"{round(request.test.test_segmental.left_leg, 1)} Lbs  {round(pounds_to_kg(request.test.test_segmental.left_leg), 1)} Kg  {round(request.test.test_segmental.left_leg_percent, 1)} %")

    # Right Leg
    pdf.set_xy(135, 140)  # Parte izquierda (título)
    pdf.cell(40, 5, "Right Leg: ", align='L')

    pdf.set_xy(155, 140)  # Parte derecha (Lbs, Kg, y %)
    pdf.cell(0, 5, f"{round(request.test.test_segmental.right_leg, 1)} Lbs  {round(pounds_to_kg(request.test.test_segmental.right_leg), 1)} Kg  {round(request.test.test_segmental.right_leg_percent, 1)} %")

    # Left Arm
    pdf.set_xy(135, 145)  # Parte izquierda (título)
    pdf.cell(40, 5, "Left Arm: ", align='L')

    pdf.set_xy(155, 145)  # Parte derecha (Lbs, Kg, y %)
    pdf.cell(0, 5, f"{round(request.test.test_segmental.left_arm, 1)} Lbs  {round(pounds_to_kg(request.test.test_segmental.left_arm), 1)} Kg  {round(request.test.test_segmental.left_arm_percent, 1)} %")

    # Right Arm
    pdf.set_xy(135, 150)  # Parte izquierda (título)
    pdf.cell(40, 5, "Right Arm: ", align='L')

    pdf.set_xy(155, 150)  # Parte derecha (Lbs, Kg, y %)
    pdf.cell(0, 5, f"{round(request.test.test_segmental.right_arm, 1)} Lbs  {round(pounds_to_kg(request.test.test_segmental.right_arm), 1)} Kg  {round(request.test.test_segmental.right_arm_percent, 1)} %")


    pdf.set_xy(103, 195)
    pdf.cell(40, 10, f"{int(request.test.test_energy.basal_metabolic_rate)} Calories/Day")
    
    pdf.set_xy(145, 195)
    pdf.cell(40, 4, f"Light {int(request.test.test_energy.light_activity)} Calories/Day")
    
    pdf.set_xy(145, 199)
    pdf.cell(40, 4, f"Moderate {int(request.test.test_energy.moderate_activity)} Calories/Day")
    
    pdf.set_xy(145, 203)
    pdf.cell(40, 4, f"Heavy {int(request.test.test_energy.heavy_activity)} Calories/Day")
    
    # pdf_bytes = bytes(pdf.output(dest='S').encode('latin-1'))
    pdf_bytes = pdf.output(dest='S')
    return pdf_bytes

def p511a(request):
    gender = "M" if request.test.test_primary.gender == 0 else "F"
    parts = request.test.test_primary.height.split(" ")
    formatted_height = f"{parts[0]} {parts[1]}\n{parts[2][:-2]} cm"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)
    pdf.set_text_color(0, 0, 0)
    
    pdf.set_xy(30, 23)
    pdf.cell(40, 10, f"{request.test.test_primary.from_field}")
    
    pdf.set_xy(30, 30)
    member_id = request.test.test_primary.member_id
    pdf.cell(40, 10, f"{'#' + str(member_id) if member_id else 'No ID'}")     
    
    pdf.set_xy(110, 23)
    pdf.cell(40, 10, f"{request.test.test_primary.creation_date.strftime('%Y/%m/%d')}")
    
    pdf.set_xy(10, 57)
    pdf.multi_cell(0, 5, f"{round(request.test.test_primary.weight, 1)} Lbs\n{round(pounds_to_kg(request.test.test_primary.weight), 1)} Kg")
    
    pdf.set_xy(40, 57)
    pdf.multi_cell(0, 5, f"{formatted_height}")
    
    pdf.set_xy(65, 57)
    pdf.cell(40, 10, f"{gender}")
    
    pdf.set_xy(83, 57)
    pdf.cell(40, 10, f"{request.test.test_primary.age}")
    
    pdf.set_xy(100, 57)
    pdf.cell(40, 10, f"{request.test.test_primary.bio_impedance}")
    
    pdf.set_xy(120, 57)
    pdf.cell(40, 10, f"{round(request.test.test_primary.bmi, 1)}")
    
    pdf.set_xy(10, 97)
    pdf.multi_cell(0, 5, f"{round(request.test.test_primary.body_fat, 1)} Lbs\n{round(pounds_to_kg(request.test.test_primary.body_fat), 1)} Kg\n{round(request.test.test_primary.body_fat_percent, 1)} %")
    
    pdf.set_xy(65, 97)
    pdf.multi_cell(0, 5, f"{round(request.test.test_primary.muscle_mass, 1)} Lbs\n{round(pounds_to_kg(request.test.test_primary.muscle_mass), 1)} Kg")
    
    pdf.set_xy(105, 97)
    pdf.multi_cell(0, 5, f"{round(request.test.test_primary.body_water, 1)} Lbs\n{round(pounds_to_kg(request.test.test_primary.body_water), 1)} Kg\n{round(request.test.test_primary.body_water_percent, 1)} %")
    
    pdf.set_xy(20, 130)
    pdf.cell(40, 10, f"{int(request.test.test_primary.visceral_fat)}")
    
    # Torso
    pdf.set_xy(65, 130)
    pdf.cell(40, 5, f"Torso: ", align='L')  
    
    pdf.set_xy(90, 130)
    pdf.cell(40, 5, f"{round(request.test.test_segmental.torso, 1)} Lbs   {round(pounds_to_kg(request.test.test_segmental.torso), 1)} Kg    {round(request.test.test_segmental.torso_percent, 1)} %", align='R')  # Parte derecha (Kg y %)

    # Left Leg
    pdf.set_xy(65, 135)
    pdf.cell(40, 5, f"Left Leg: ", align='L')  
    pdf.set_xy(90, 135)
    pdf.cell(40, 5, f"{round(request.test.test_segmental.left_leg, 1)} Lbs   {round(pounds_to_kg(request.test.test_segmental.left_leg), 1)} Kg    {round(request.test.test_segmental.left_leg_percent, 1)} %", align='R')  # Parte derecha (Kg y %)

    # Right Leg
    pdf.set_xy(65, 140)
    pdf.cell(40, 5, f"Right Leg: ", align='L')  
    pdf.set_xy(90, 140)
    pdf.cell(40, 5, f"{round(request.test.test_segmental.right_leg, 1)} Lbs   {round(pounds_to_kg(request.test.test_segmental.right_leg), 1)} Kg    {round(request.test.test_segmental.right_leg_percent, 1)} %", align='R')  # Parte derecha (Kg y %)

    # Left Arm
    pdf.set_xy(65, 145)
    pdf.cell(40, 5, f"Left Arm: ", align='L')  
    pdf.set_xy(90, 145)
    pdf.cell(40, 5, f"{round(request.test.test_segmental.left_arm, 1)} Lbs   {round(pounds_to_kg(request.test.test_segmental.left_arm), 1)} Kg    {round(request.test.test_segmental.left_arm_percent, 1)} %", align='R')  # Parte derecha (Kg y %)

    # Right Arm
    pdf.set_xy(65, 150)
    pdf.cell(40, 5, f"Right Arm: ", align='L')  
    pdf.set_xy(90, 150)
    pdf.cell(40, 5, f"{round(request.test.test_segmental.right_arm, 1)} Lbs   {round(pounds_to_kg(request.test.test_segmental.right_arm), 1)} Kg    {round(request.test.test_segmental.right_arm_percent, 1)} %", align='R')  # Parte derecha (Kg y %)

    
    pdf.set_xy(20, 177)
    pdf.cell(40, 10, f"{request.test.test_energy.basal_metabolic_rate} Calories/Day")
    
    pdf.set_xy(65, 180)
    pdf.cell(40, 5, f"Light: {int(request.test.test_energy.light_activity)} Calories/Day")
    pdf.set_xy(65, 185)
    pdf.cell(40, 5, f"Moderate: {int(request.test.test_energy.moderate_activity)} Calories/Day")
    pdf.set_xy(65, 190)
    pdf.cell(40, 5, f"Heavy: {int(request.test.test_energy.heavy_activity)} Calories/Day")
    
    # pdf_bytes = bytes(pdf.output(dest='S').encode('latin-1'))
    pdf_bytes = pdf.output(dest='S')
    return pdf_bytes

def p055b(request, company_name=""):
    gender = "M" if request.test.test_primary.gender == 0 else "F"
    parts = request.test.test_primary.height.split(" ")
    formatted_height = f"{parts[0]} {parts[1]} {parts[2][:-2]} cm"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)
    pdf.set_text_color(0, 0, 0)
    
    pdf.set_xy(30, 80)
    pdf.multi_cell(0, 7, f"Assessment Prepared By\n{request.test.test_primary.by_field}")
    
    pdf.set_xy(30, 90)
    pdf.cell(40, 10, f"{company_name}")
    
    pdf.set_xy(30, 100)
    pdf.multi_cell(0, 7, f"Assessment Prepared For\n{request.test.test_primary.from_field}")
    
    pdf.set_xy(130, 80)
    pdf.multi_cell(0, 7, f"Date:\n{request.test.test_primary.creation_date.strftime('%Y/%m/%d')}")
    
    pdf.set_xy(130, 100)
    member_id = request.test.test_primary.member_id
    pdf.multi_cell(0, 7, f"{'ID No #' + str(member_id) if member_id else 'No ID'}")     

    pdf.set_xy(30, 125)
    pdf.cell(40, 10, f"Current Body Weight:    {round(request.test.test_primary.weight, 1)} Lbs {round(pounds_to_kg(request.test.test_primary.weight), 1)} Kg")
    
    pdf.set_xy(30, 135)
    pdf.cell(40, 10, f"Body Mass Index:    {round(request.test.test_primary.bmi, 1)}")
    
    pdf.set_xy(30, 115)
    pdf.cell(40, 10, f"Gender: {gender}")
    
    pdf.set_xy(80, 115)
    pdf.multi_cell(0, 7, f"Hgt: {formatted_height}")
    
    pdf.set_xy(130, 113)
    pdf.cell(40, 10, f"Age: {request.test.test_primary.age}")
    
    pdf.set_xy(140, 165)
    pdf.multi_cell(0, 3.5, f"{round(request.test.test_primary.body_fat, 1)} Lbs \n{round(pounds_to_kg(request.test.test_primary.body_fat), 1)} Kg \n{round(request.test.test_primary.body_fat_percent, 1)} %")
    
    pdf.set_xy(140, 172)
    pdf.cell(40, 10, f"{int(request.test.test_primary.visceral_fat)} VF")
    
    pdf.set_xy(140, 179)
    pdf.multi_cell(0, 4, "Visceral Fat Ranges \nNormal:    1 - 9\nHigh:    10 - 14\nVery High:    15+")
    
    pdf.set_xy(140, 217)
    pdf.multi_cell(0, 5, f"{round(request.test.test_primary.body_water, 1)} lbs\n{round(pounds_to_kg(request.test.test_primary.body_water), 1)} Kg\n{round(request.test.test_primary.body_water_percent, 1)} %")
    
    pdf.add_page() # Second page
    
    pdf.set_xy(120, 155)
    pdf.multi_cell(0, 5, f"{round(request.test.test_primary.lean_mass, 1)} Lbs\n{round(pounds_to_kg(request.test.test_primary.lean_mass), 1)} Kg\n{round(request.test.test_primary.lean_mass_percent, 1)} %")
    
    pdf.add_page() # Third page
    
    pdf.set_xy(130, 10)
    pdf.multi_cell(0, 7, f"{int(request.test.test_energy.basal_metabolic_rate)} Calories/Day required to \nmaintain vital body functions")
    
    pdf.set_xy(130, 230)
    pdf.multi_cell(0, 5, f"Very Light Activity: {int(request.test.test_energy.very_light_activity)} Calories/Day\nLight Activity: {int(request.test.test_energy.light_activity)} Calories/Day\nModerate Activity: {int(request.test.test_energy.moderate_activity)} Calories/Day\nHeavy Activity: {int(request.test.test_energy.heavy_activity)} Calories/Day\nVery Heavy Activity: {int(request.test.test_energy.very_heavy_activity)} Calories/Day")
    
    pdf.add_page() # Fourth page
    
    pdf.set_xy(60, 90)
    pdf.cell(40, 10, f"You are {round(request.test.test_primary.aiw, 1)}% over your ideal weight.")
    
    # pdf_bytes = bytes(pdf.output(dest='S').encode('latin-1'))
    pdf_bytes = pdf.output(dest='S')
    return pdf_bytes

def combine_pdf(pdf1: bytes, pdf2: bytes) -> bytes:
    merger = PdfWriter()
    merger.append(io.BytesIO(pdf1))
    merger.append(io.BytesIO(pdf2))
    output = io.BytesIO()
    merger.write(output)
    merger.close()
    return output.getvalue()