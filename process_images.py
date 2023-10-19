import cv2
import pytesseract
import os
from pytesseract import Output

# Ensure the output_step2 directory exists
os.makedirs('output_step2', exist_ok=True)

def process_images(image_folder):
    all_pages_data = []
    images = sorted(os.listdir(image_folder))  # Ensure pages are processed in order
    
    for image_file in images:
        if not image_file.endswith('.png'):
            continue  # Skip non-PNG files
        
        image_path = os.path.join(image_folder, image_file)
        image = cv2.imread(image_path)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Get text data with bounding boxes
        text_data = pytesseract.image_to_data(gray_image, output_type=Output.DICT)
        
        page_data = {
            "page_number": int(image_file.split('_')[1].split('.')[0]),
            "content": []
        }
        
        # Thresholding to get binary image
        _, thresh = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Morphological operations to merge nearby contours
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (60, 60))
        merged_contours = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # Find contours on the morphologically processed image
        contours, _ = cv2.findContours(merged_contours, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # Sort contours by y-axis position
        contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])  # Sorting by y value of boundingRect

        for i, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)
            if w > 100 and h > 100:  # Consider image blocks with reasonable size
                block_image = gray_image[y:y+h, x:x+w]
                block_file_name = f'output_step2/page_{page_data["page_number"]}_block_{i + 1}.png'
                cv2.imwrite(block_file_name, block_image)
                page_data["content"].append({"type": "block", "data": block_image, "position": (x, y, w, h)})
        
        all_pages_data.append(page_data)
    
    return all_pages_data

# Specify the image folder
image_folder = 'output_images'
processed_data = process_images(image_folder)
