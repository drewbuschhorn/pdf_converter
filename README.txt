Converts PDF to text by image processing.

Needs a few weird exe/dll things to work on windows besides pip requirements: popper, tesseract, also probably pytorch cuda.

Use Briss.exe to break PDF down from double breasted scan to single breasted scan or other clipping as needed. Once in purely vertical read format:

Run in order with a file called input.pdf:
convert.py (to png, maybe play with ppi setting in the future, didn't seem to make a different upping to 600dpi from 200dpi)
process_images.py (to image blocks)
process_blocks.py (image blocks to text block using huggingface OCR pipeline, or image block if text seems bad)
process_blocks_to_clean.py (text blocks to punctuated text blocks using a punctuation helper, and copy over images)
blocks_to_books.py (resizes images / jpeg, combines text and makes epub)

should output an epub.