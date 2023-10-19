import os
from deepmultilingualpunctuation import PunctuationModel

model = PunctuationModel()

def restore_punctuation(text):
    try:
        # Attempt to restore punctuation in the entire text block
        first_pass = model.restore_punctuation(text)
        result = model.restore_punctuation(first_pass)
        print(result)
        return result
    except:
        # If the text block is too large, split it into chunks of up to 2048 characters, respecting word boundaries
        chunks = [text[i:i+512] for i in range(0, len(text), 512)]
        result = ""
        for chunk in chunks:
            first_pass = model.restore_punctuation(chunk)
            result += model.restore_punctuation(first_pass)
        print(result)
        return result

def get_sort_key(file_name):
    # Extract the page and block numbers from the file name
    parts = file_name.split('_')
    page_number = int(parts[1])
    block_number = int(parts[3].split('.')[0])
    return (page_number, block_number)

def copy_png_files(input_dir, output_dir):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Copy the PNG files to the output directory
    for file_name in [f for f in os.listdir(input_dir) if f.endswith('.png')]:
        input_file_path = os.path.join(input_dir, file_name)
        output_file_path = os.path.join(output_dir, file_name)
        with open(input_file_path, 'rb') as input_file:
            with open(output_file_path, 'wb') as output_file:
                output_file.write(input_file.read())

def process_text_files(input_dir, output_dir):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # List all text files in the input directory and sort them by page and block numbers
    files = sorted([f for f in os.listdir(input_dir) if f.endswith('.txt')], key=get_sort_key)
    copy_png_files(input_dir, output_dir)

    for i, file_name in enumerate(files):
        input_file_path = os.path.join(input_dir, file_name)
        output_file_path = os.path.join(output_dir, file_name)

        # Read the current text file
        with open(input_file_path, 'r', encoding='utf-8') as input_file:
            text_content = input_file.read()

        # If there's a next text file, read the first few words from it
        if i + 1 < len(files):
            next_file_path = os.path.join(input_dir, files[i + 1])
            with open(next_file_path, 'r', encoding='utf-8') as next_file:
                next_text_content = next_file.read()
            extra_words = ' '.join(next_text_content.split()[:5])  # Assuming 5 words from the next file
            text_content += ' ' + extra_words

        # Restore punctuation
        processed_text = restore_punctuation(text_content)

        # Remove the extra words from the end of the processed text
        if i + 1 < len(files):
            processed_text = processed_text[:-(len(extra_words) + 1)]

        # Save the processed text to the output directory
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(processed_text)

# Define the input and output directories
input_dir = 'output_step3'
output_dir = 'output_step4'

# Process the text files
process_text_files(input_dir, output_dir)
