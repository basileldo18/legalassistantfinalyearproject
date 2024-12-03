from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas

# Define the file name and dimensions
pdf_file = "generated_pdf_example.pdf"
page_width, page_height = A4

# Create a new canvas
c = canvas.Canvas(pdf_file, pagesize=A4)

# Set the title and basic styles
c.setFont("Helvetica-Bold", 18)
c.drawString(100, page_height - 100, "PDF Generation Example")
c.setFont("Helvetica", 12)

# Add some sample content
content = [
    "This PDF was generated using Python!",
    "You can add more text, images, tables, and graphics as needed.",
    "Here is an example of how to use reportlab for PDF generation.",
]

y_position = page_height - 150
for line in content:
    c.drawString(100, y_position, line)
    y_position -= 20

# Add a line for separation
c.setStrokeColor(colors.gray)
c.line(100, y_position - 10, page_width - 100, y_position - 10)

# Close and save the PDF
c.showPage()
c.save()

print(f"PDF '{pdf_file}' created successfully!")
