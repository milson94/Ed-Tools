from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from PIL import Image, ImageOps
import os

def add_footer_to_pdfs(pdf_files, footer_image, upload_folder):
    # Save the footer image
    footer_path = os.path.join(upload_folder, 'footer.png')
    footer_image.save(footer_path)

    # Open the footer image with Pillow to handle transparency
    with Image.open(footer_path) as img:
        # Ensure the image has an alpha channel (transparency)
        img = img.convert("RGBA")
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
                can = canvas.Canvas(packet, pagesize=A4)

                # Calculate the position for the footer
                page_width, page_height = A4
                footer_scale = page_width / footer_width  # Scale footer to fit page width
                scaled_footer_height = footer_height * footer_scale

                # Create a blank image with transparency
                blank_image = Image.new("RGBA", (int(page_width), int(scaled_footer_height)), (0, 0, 0, 0))
                # Resize the footer image to fit the page width
                resized_footer = img.resize((int(page_width), int(scaled_footer_height)), Image.Resampling.LANCZOS)
                # Composite the footer onto the blank image
                blank_image.paste(resized_footer, (0, 0), resized_footer)

                # Save the composited image as a temporary file
                temp_footer_path = os.path.join(upload_folder, 'temp_footer.png')
                blank_image.save(temp_footer_path, "PNG")

                # Draw the composited image onto the PDF
                # Adjust the X-axis position by 5 pixels to the right
                x_position = 5  # Move 5px to the right
                can.drawImage(
                    temp_footer_path,
                    x_position,  # Adjusted X position
                    0,  # Y position (bottom-aligned)
                    width=page_width,  # Scale footer to fit page width
                    height=scaled_footer_height,  # Maintain aspect ratio
                    mask='auto'  # Preserve transparency
                )
                can.save()

                # Merge the footer with the original page
                packet.seek(0)
                footer_pdf = PdfReader(packet)
                page.merge_page(footer_pdf.pages[0])
                pdf_writer.add_page(page)

                # Clean up the temporary footer file
                os.remove(temp_footer_path)

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