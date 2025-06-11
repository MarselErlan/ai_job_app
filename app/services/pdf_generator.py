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
import os
from loguru import logger
from app.utils.debug_utils import debug_performance

# Configure Loguru for this module
logger.add(
    "logs/pdf_generator.log",
    rotation="1 day",
    retention="7 days",
    level="DEBUG",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

@debug_performance
def save_resume_as_pdf(text: str, filename: str = "tailored_resume.pdf") -> str:
    """
    Convert resume text to a professionally formatted PDF.
    
    Args:
        text (str): Resume text content to convert
        filename (str): Name of the output PDF file
        
    Returns:
        str: Path to the generated PDF file
    """
    logger.info(f"Starting PDF generation for {filename}")
    logger.debug(f"Input text length: {len(text)} characters")
    
    try:
        # Create PDF object
        logger.debug("Initializing PDF document")
        pdf = FPDF()
        
        # Add the first page to the PDF
        pdf.add_page()
        logger.debug("Added first page to PDF")
        
        # Set up automatic page breaks with proper margins
        pdf.set_auto_page_break(auto=True, margin=15)
        logger.debug("Configured auto page breaks with 15pt margin")
        
        # Set the font for the entire document
        pdf.set_font("Arial", size=12)
        logger.debug("Set document font to Arial 12pt")

        # Split the resume text into individual lines for processing
        lines = text.split("\n")
        logger.debug(f"Split content into {len(lines)} lines")
        
        # Process each line of the resume
        page_count = 1
        line_count = 0
        
        for i, line in enumerate(lines, 1):
            # Check if the line is empty (just whitespace)
            if not line.strip():
                # Add vertical spacing for empty lines
                pdf.ln(5)
                logger.debug(f"Added vertical spacing at line {i}")
            else:
                # Process non-empty lines with text wrapping
                wrapped_lines = textwrap.wrap(line, width=100)
                logger.debug(f"Line {i}: Wrapped into {len(wrapped_lines)} segments")
                
                for wrapped_line in wrapped_lines:
                    try:
                        # Handle character encoding
                        encoded_line = wrapped_line.encode('latin-1', 'replace').decode('latin-1')
                        
                        # Add the line to the PDF
                        pdf.cell(0, 10, encoded_line, ln=True)
                        line_count += 1
                        
                        # Check if we've moved to a new page
                        if pdf.page_no() > page_count:
                            page_count = pdf.page_no()
                            logger.info(f"Added new page: {page_count}")
                            
                    except Exception as e:
                        logger.warning(f"Issue processing line {i}: {str(e)}")
                        # Continue processing despite the error
                        continue

        # Create the output directory if it doesn't exist
        os.makedirs("uploads", exist_ok=True)
        
        # Create the full path where the PDF will be saved
        output_path = f"uploads/{filename}"
        logger.debug(f"Preparing to save PDF to: {output_path}")
        
        # Save the PDF to the file system
        pdf.output(output_path)
        
        # Log success with file details
        file_size = os.path.getsize(output_path) / 1024  # Convert to KB
        logger.info(f"PDF generated successfully:")
        logger.info(f"- Path: {output_path}")
        logger.info(f"- Size: {file_size:.2f}KB")
        logger.info(f"- Pages: {page_count}")
        logger.info(f"- Lines processed: {line_count}")
        
        # Return the path so other parts of the system can find the PDF
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to generate PDF: {str(e)}")
        raise
