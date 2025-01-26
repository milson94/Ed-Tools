from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4  # Use A4 page size
from reportlab.pdfgen import canvas
from io import BytesIO
from PIL import Image
import os

def add_footer_to_pdfs(pdf_files, footer_image, upload_folder):
    # Save the footer image
    footer_path = os.path.join(upload_folder, 'footer.png')
    footer_image.save(footer_path)

    # Get the dimensions of the footer image
    with Image.open(footer_path) as img:
        footer_width, footer_height = img.size

    # Process each PDF file
    output_pdfs = []
    for pdf_file in pdf_files:
        if pdf_file.filename.endswith('.pdf'):
            # Read the PDF
            pdf_reader = PdfReader(pdf_file)
            pdf_writer = PdfWriter()

            # Add the footer to each page
            for page in pdf_reader.pages:
                # Create a new PDF page with the footer
                packet = BytesIO()
                can = canvas.Canvas(packet, pagesize=A4)  # Use A4 page size

                # Calculate the position for the footer
                page_width, page_height = A4
                footer_scale = page_width / footer_width  # Scale footer to fit page width
                scaled_footer_height = footer_height * footer_scale

                # Draw the footer at the bottom of the page
                can.drawImage(
                    footer_path,
                    0,  # X position (left-aligned)
                    0,  # Y position (bottom-aligned)
                    width=page_width,  # Scale footer to fit page width
                    height=scaled_footer_height,  # Maintain aspect ratio
                    preserveAspectRatio=True,  # Prevent squashing
                    anchor='sw'  # Anchor to the bottom-left corner
                )
                can.save()

                # Merge the footer with the original page
                packet.seek(0)
                footer_pdf = PdfReader(packet)
                page.merge_page(footer_pdf.pages[0])
                pdf_writer.add_page(page)

            # Save the modified PDF
            output_path = os.path.join(upload_folder, f'modified_{pdf_file.filename}')
            with open(output_path, 'wb') as output_pdf:
                pdf_writer.write(output_pdf)
            output_pdfs.append(output_path)

    # Merge all modified PDFs into one
    merger = PdfWriter()
    for pdf_path in output_pdfs:
        merger.append(pdf_path)
    final_output_path = os.path.join(upload_folder, 'final_output.pdf')
    with open(final_output_path, 'wb') as final_output:
        merger.write(final_output)
    merger.close()

    return final_output_path