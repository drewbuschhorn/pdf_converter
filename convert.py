import os
from pdf2image import convert_from_path

def convert_pdf_to_png(pdf_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    # Convert PDF pages to images
    images = convert_from_path(pdf_path, poppler_path=r"C:\Users\drewb\Downloads\poppler-23.08.0-0\poppler-23.08.0\Library\bin", dpi=300)

    # Save each image to the output folder
    for index, image in enumerate(images):
        image.save(f'{output_folder}/page_{index + 1}.png', 'PNG')

# Specify the input PDF file and the output folder
pdf_path = 'input.pdf'
output_folder = 'output_images'
convert_pdf_to_png(pdf_path, output_folder)