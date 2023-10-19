import ebooklib
from ebooklib import epub
import os
import cv2
import markdown
import argparse

# Define and parse the command line arguments
parser = argparse.ArgumentParser(description='Convert a folder of text and image files into an EPUB book.')
parser.add_argument('--input-folder', dest='input_folder', default='output_step3',
                    help='Path to the folder containing the files to be included in the EPUB book (default: output_step3)')
args = parser.parse_args()

# Use the input_folder specified on the command line, or the default value
input_folder = args.input_folder

def resize_image(image, max_dimensions=(600, 800)):
    height, width, _ = image.shape
    max_width, max_height = max_dimensions
    
    # Calculate the scaling factor needed to keep the image within max_dimensions
    scaling_factor = min(max_width / width, max_height / height)
    
    # If the scaling factor is greater than 1, it means the image is smaller than max_dimensions,
    # so no resizing is needed. Otherwise, resize the image while maintaining the aspect ratio.
    if scaling_factor < 1:
        new_width = int(width * scaling_factor)
        new_height = int(height * scaling_factor)
        resized_image = cv2.resize(image, (new_width, new_height))
        return resized_image
    else:
        return image  # return original image if it's already within max_dimensions

# Create a new EPUB book
book = epub.EpubBook()

# Set the title and author
book.set_title('Converted Book')
book.add_author('Author Name')

# Get a sorted list of the files in the output_step3 directory
files = sorted(os.listdir(input_folder), key=lambda x: (int(x.split('_')[1]), int(x.split('_')[3].split('.')[0])))

# Initialize a list to hold the EPUB chapters
chapters = []

# Initialize a variable to hold the current chapter
current_chapter = None
current_chapter_number = 0

# Process each file
for file_name in files:
    file_path = os.path.join(input_folder, file_name)
    page_number = int(file_name.split('_')[1])

    # If this is a new chapter (every 10th page), create a new chapter
    if page_number % 10 == 0 or current_chapter is None:
        current_chapter_number += 1
        chapter_title = f'Chapter {current_chapter_number}'
        current_chapter = epub.EpubHtml(title=chapter_title, file_name=f'{chapter_title}.xhtml')
        chapters.append(current_chapter)

    # Determine if the file is text or image
    if file_name.endswith('.txt'):
        # Read the text file
        with open(file_path, 'r', encoding='utf-8') as text_file:
            text_content = text_file.read()
            quotes = ['"', "'", '\u2018', '\u2019', '\u201C', '\u201D']
            if text_content and (text_content[0] in quotes):
                text_content = ' ' + text_content[1:]
            if text_content and (text_content[-1] in quotes):
                text_content = text_content[:-1] + ' '
        # Convert Markdown to HTML
        try:
            html_content = markdown.markdown(text_content)
        except:
            html_content = text_content
        # Add the text content to the current chapter
        if current_chapter.content is None:
            current_chapter.content = f''
        if html_content:
            current_chapter.content += f'{html_content}'
    else:
        original_ppi = 300.0  # replace with the original PPI
        downscaling_factor = original_ppi / 72.0

        # Assume the file is an image
        image = cv2.imread(file_path)
        # Resize the image to keep it within Kindle-friendly dimensions (600x800) while maintaining the aspect ratio
        resized_image = resize_image(image)
        # Convert the resized image back to PNG
        _, buffer = cv2.imencode('.jpg', resized_image, [cv2.IMWRITE_JPEG_QUALITY, 50])
        # Create an EpubImage item
        image_file_name = f'image_{file_name.split("_")[1]}_{file_name.split("_")[3]}'
        image_item = epub.EpubImage()
        image_item.file_name = image_file_name
        image_item.content = buffer.tobytes()
        book.add_item(image_item)
        # Include the image in the current chapter
        if current_chapter.content is None:
            current_chapter.content = f''
        current_chapter.content += f'<img src="{image_file_name}" alt="Image"/>'

# Add the chapters to the book
for chapter in chapters:
    book.add_item(chapter)

# Define the book spine (order of the book items)
book.spine = ['nav'] + chapters

# Define the table of contents
book.toc = chapters

# Write the EPUB file
epub.write_epub('output.epub', book)


# At the end of your script:
if __name__ == '__main__':
    pass
    # Process the files and create the EPUB book
    # Your existing code for processing the files and creating the EPUB book goes here