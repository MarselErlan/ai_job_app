# File: app/services/pdf_generator.py

from fpdf import FPDF
import textwrap

def save_resume_as_pdf(text: str, filename: str = "tailored_resume.pdf") -> str:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    lines = text.split("\n")
    for line in lines:
        if not line.strip():
            pdf.ln(5)
        else:
            for wrapped_line in textwrap.wrap(line, width=100):
                wrapped_line = wrapped_line.encode('latin-1', 'replace').decode('latin-1')
                pdf.cell(0, 10, wrapped_line, ln=True)


    output_path = f"uploads/{filename}"
    pdf.output(output_path)
    return output_path
