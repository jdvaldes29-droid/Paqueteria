from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from datetime import date
from app.supabase_client import supabase

hoy = date.today().strftime("%Y-%m-%d")
archivo_pdf = f"reporte_paquetes_{hoy}.pdf"

doc = SimpleDocTemplate(archivo_pdf, pagesize=A4)
styles = getSampleStyleSheet()
contenido = []

contenido.append(Paragraph(
    f"<b>REPORTE DIARIO DE PAQUETERÍA</b><br/>Fecha: {hoy}",
    styles["Title"]
))

response = supabase.table("paquetes").select("*").execute()

total = len(response.data)
entregados = len([p for p in response.data if p["estatus"] == "ENTREGADO"])

tabla = Table([
    ["Total Paquetes", "Entregados"],
    [total, entregados]
])

tabla.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ("GRID", (0,0), (-1,-1), 1, colors.black),
]))

contenido.append(tabla)

doc.build(contenido)

print("Reporte generado:", archivo_pdf)