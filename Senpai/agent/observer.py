import pytesseract
from PIL import Image

class Observer:
    def ocr_image(self, image_path):
        return pytesseract.image_to_string(Image.open(image_path))
