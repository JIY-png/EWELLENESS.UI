---
name: generate-pdf
description: >-
  Use this skill when the user asks to generate a new PDF report or add a new PDF generation feature to the application. It provides the standard ReportLab styling and boilerplate used in the E-Wellness project.
---

# PDF Generator Scaffold

When creating a new PDF generation endpoint in the E-Wellness Flask application, follow these guidelines to maintain consistency.

## Steps to create a new PDF report:

1. **Import Required ReportLab Modules**:
   Ensure `app.py` has the necessary ReportLab imports:
   ```python
   from reportlab.lib import colors
   from reportlab.lib.pagesizes import letter
   from reportlab.lib.styles import getSampleStyleSheet
   from reportlab.lib.units import inch
   from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
   from io import BytesIO
   ```

2. **Standard Styling**:
   Use the following baseline styling for tables:
   ```python
   style = TableStyle([
       ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')), # Header background
       ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), # Header text
       ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
       ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
       ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
       ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')), # Row background
       ('GRID', (0, 0), (-1, -1), 1, colors.black)
   ])
   ```

3. **Response Handling**:
   Always return the generated PDF as a downloadable file via Flask's `send_file`:
   ```python
   buffer = BytesIO()
   doc = SimpleDocTemplate(buffer, pagesize=letter)
   # ... build PDF elements ...
   doc.build(elements)
   buffer.seek(0)
   return send_file(buffer, as_attachment=True, download_name="report.pdf", mimetype='application/pdf')
   ```
