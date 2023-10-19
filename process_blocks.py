import re
import cv2
from numpy import average
import os
from spellchecker import SpellChecker
from PIL import Image
from transformers import NougatProcessor, VisionEncoderDecoderModel
import torch

Image.MAX_IMAGE_PIXELS = 1000000000

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f'Using device: {device}')

# Constants and Initializations
pattern = re.compile(r'(?:[aeiouAEIOU]{5,})+')
processor = NougatProcessor.from_pretrained("facebook/nougat-base")
model = VisionEncoderDecoderModel.from_pretrained("facebook/nougat-base")
model.to(device)

os.makedirs('output_step3', exist_ok=True)

def add_border_to_image(image, border_size=10):
    """Add border to a given image."""
    return cv2.copyMakeBorder(image, border_size, border_size, border_size, border_size, cv2.BORDER_CONSTANT, value=[255, 255, 255])

def hf_ocr(image_np):
    image = Image.fromarray(image_np).convert("RGB")
    processed_data = processor(image, return_tensors="pt")

    pixel_values = processed_data.pixel_values.to(device)

    outputs = model.generate(
        pixel_values,
        min_length=10,
        max_new_tokens=1000,
        bad_words_ids=[[processor.tokenizer.unk_token_id]],
    )
    sequence = processor.batch_decode(outputs, skip_special_tokens=True)[0]
    sequence = processor.post_process_generation(sequence, fix_markdown=False)

    print ("output: ", sequence)
    return sequence

def ocr_and_sort_blocks(input_folder, output_folder):
    spell = SpellChecker()
    files = sorted(os.listdir(input_folder), key=lambda x: (int(x.split('_')[1]), int(x.split('_')[3].split('.')[0])))
    
    for file_name in files:
        file_path = os.path.join(input_folder, file_name)
        image = cv2.imread(file_path)
        image = add_border_to_image(image)
        
        # Scale up the image to 300 PPI
        original_ppi = 72.0
        desired_ppi = 600.0
        scale_factor = desired_ppi / original_ppi
        new_dimensions = (int(image.shape[1] * scale_factor), int(image.shape[0] * scale_factor))
        upscaled_image = cv2.resize(image, new_dimensions, interpolation=cv2.INTER_CUBIC)
        
        #gray_image = cv2.cvtColor(upscaled_image, cv2.COLOR_BGR2GRAY)
        
        # Perform OCR to extract text
        #extracted_text = pytesseract.image_to_string(gray_image, config='--psm 6 --oem 1')
        try:
            extracted_text = hf_ocr(upscaled_image)
            extracted_text = extracted_text.replace('/', ' / ')
            extracted_text = extracted_text.replace('(', ' ( ')
            extracted_text = extracted_text.replace(')', ' ) ')
            extracted_text = extracted_text.replace('[', ' [ ')
            extracted_text = extracted_text.replace(']', ' ] ')
            extracted_text = extracted_text.replace('{', ' { ')
            extracted_text = extracted_text.replace('}', ' } ')
            extracted_text = extracted_text.replace('«', ' « ')
            extracted_text = extracted_text.replace('»', ' » ')
            extracted_text = extracted_text.replace('…', ' … ')

            words = extracted_text.split()
            total_words = len(words)
            
            # Check spelling to estimate the number of misspelled words
            misspelled = spell.unknown(words)
            misspelled_count = len(misspelled)
            
            # Correct spelling
            corrected_text = extracted_text
            corrected_text = re.sub(r'  ([A-Z])', r'.  \1', corrected_text)

            for word in misspelled:
                correct = spell.correction(word)
                if correct:
                    corrected_text = corrected_text.replace(word, correct)
                else:
                    # If no correction is found, replace with empty string
                    print (f'No correction found for {word}')
            
            # Replace double newlines with period and space
            corrected_text = corrected_text.replace('\n\n', '. ')
            corrected_text = corrected_text.replace('\n', ' ')
            
            average_word_length = average([len(word) for word in words]) if words else 0
            
            print (f'File: {file_name}, Total words: {total_words}, Misspelled words: {misspelled_count},\
                    Average word length: {average_word_length} Pattern search: {pattern.search(corrected_text)}')

            if total_words > 20 and (misspelled_count / total_words) <= 0.8 and average_word_length >= 4.0 \
            and (pattern.search(corrected_text) is None):
                # Likely a text block
                output_file_name = f'{output_folder}/{file_name.replace(".png", ".txt")}'
                with open(output_file_name, 'w', encoding='utf-8') as text_file:
                    text_file.write(corrected_text + " ")
            else:
                # Likely an image block
                output_file_name = f'{output_folder}/{file_name}'
                cv2.imwrite(output_file_name, image)
        except Exception as e:
            print(f'Error processing {file_name} - {e}')
            output_file_name = f'{output_folder}/{file_name}'
            cv2.imwrite(output_file_name, image)

# Specify the input and output folders
input_folder = 'output_step2'
output_folder = 'output_step3'
ocr_and_sort_blocks(input_folder, output_folder)
