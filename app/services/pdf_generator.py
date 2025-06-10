# File: app/services/pdf_generator.py
"""
PDF GENERATOR SERVICE - Convert tailored resume text back into professional PDF

After GPT-4 tailors your resume text, this service converts it back into a 
professionally formatted PDF that you can submit to employers.

The Process:
1. Takes the tailored resume text from GPT-4
2. Splits it into lines and handles formatting
3. Uses FPDF library to create a clean PDF
4. Handles text wrapping and character encoding
5. Saves the PDF to the uploads directory

This ensures your AI-tailored resume looks professional when submitted.
"""

from fpdf import FPDF  # Python library for PDF creation
import textwrap       # For wrapping long lines of text

def save_resume_as_pdf(text: str, filename: str = "tailored_resume.pdf") -> str:
    pdf = FPDF()
    
    # Add the first page to the PDF
    pdf.add_page()
    
    # Set up automatic page breaks with proper margins
    # If content goes past the bottom margin, it automatically creates a new page
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Set the font for the entire document
    # Arial is professional and widely supported
    # Size 12 is readable without being too large
    pdf.set_font("Arial", size=12)

    # Split the resume text into individual lines for processing
    lines = text.split("\n")
    
    # Process each line of the resume
    for line in lines:
        # Check if the line is empty (just whitespace)
        if not line.strip():
            # Add vertical spacing for empty lines
            # This creates visual breaks between sections
            pdf.ln(5)
        else:
            # Process non-empty lines with text wrapping
            # textwrap.wrap() breaks long lines into multiple shorter lines
            # width=100 means roughly 100 characters per line (fits well on page)
            for wrapped_line in textwrap.wrap(line, width=100):
                # Handle character encoding issues
                # PDFs have limited character support, so we convert problematic characters
                # encode('latin-1', 'replace') converts to PDF-compatible characters
                # replace mode substitutes unsupported characters with similar ones
                wrapped_line = wrapped_line.encode('latin-1', 'replace').decode('latin-1')
                
                # Add the line to the PDF
                # cell(0, 10, text, ln=True) creates a full-width cell with 10pt height
                # ln=True moves to the next line after adding this text
                pdf.cell(0, 10, wrapped_line, ln=True)

    # Create the full path where the PDF will be saved
    output_path = f"uploads/{filename}"
    
    # Save the PDF to the file system
    pdf.output(output_path)
    
    # Return the path so other parts of the system can find the PDF
    return output_path
