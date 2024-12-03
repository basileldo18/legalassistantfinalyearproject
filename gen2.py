from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import io



def generate_pdf(title,content):
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    page_width, page_height = A4
    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, page_height - 100, title)
    c.setFont("Helvetica", 12)
    y_position = page_height - 150
    for line in content.splitlines():
        c.drawString(100, y_position, line)
        y_position -= 20
    c.setStrokeColor(colors.gray)
    c.line(100, y_position - 10, page_width - 100, y_position - 10)
    c.showPage()
    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer

