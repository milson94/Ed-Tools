from PyPDF2 import PdfMerger
import os

def merge_pdfs(pdf_files, output_filename, upload_folder):
    """
    Merge multiple PDF files into a single PDF.

    Args:
        pdf_files (list): List of uploaded PDF files.
        output_filename (str): Name of the output PDF file.
        upload_folder (str): Directory to save the merged PDF.

    Returns:
        str: Path to the merged PDF file.
    """
    # Ensure the output filename has a .pdf extension
    if not output_filename.endswith('.pdf'):
        output_filename += '.pdf'

    # Create a PdfMerger object
    merger = PdfMerger()

    try:
        # Append each PDF file to the merger
        for pdf_file in pdf_files:
            if pdf_file.filename.endswith('.pdf'):
                merger.append(pdf_file)

        # Save the merged PDF
        final_output_path = os.path.join(upload_folder, output_filename)
        with open(final_output_path, 'wb') as final_output:
            merger.write(final_output)

        return final_output_path
    except Exception as e:
        raise Exception(f"Error merging PDFs: {str(e)}")
    finally:
        merger.close()