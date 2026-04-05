import logging

logger = logging.getLogger(__name__)

def process_image(image_bytes: bytes) -> str:
    """Распознаёт текст из изображения через EasyOCR (модели ru+en)."""
    import easyocr

    reader = easyocr.Reader(["ru", "en"], gpu=False)
    result = reader.readtext(image_bytes, detail=0, paragraph=True)

    text = "\n".join(result)
    return text
