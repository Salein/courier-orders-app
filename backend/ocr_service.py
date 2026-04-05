"""OCR service using EasyOCR. Extracts raw text from receipt images."""

import io
import logging
from typing import NewType, Tuple

import easyocr
from PIL import Image

logger = logging.getLogger(__name__)

# Be explicit about what we return
OCRText = NewType("OCRText", str)


class OCRProcessor:
    """Wrapper around EasyOCR for receipt processing."""

    def __init__(self, languages: list[str] | None = None) -> None:
        self.languages = languages or ["ru", "en"]
        self._reader = None
        self._initialize_reader()

    def _initialize_reader(self) -> None:
        """Initialize EasyOCR reader (downloading models if needed)."""
        try:
            self._reader = easyocr.Reader(self.languages, gpu=False)
            logger.info("EasyOCR initialized with languages: %s", self.languages)
        except Exception as e:
            logger.error("Failed to initialize EasyOCR: %s", e)
            raise

    def extract_text(self, image_bytes: bytes) -> Tuple[OCRText, float]:
        """
        Extract text from an image.

        Args:
            image_bytes: Raw image file bytes (JPEG/PNG)

        Returns:
            Tuple of (extracted_text, average_confidence)
        """
        if self._reader is None:
            self._initialize_reader()

        # Load image with PIL
        try:
            image = Image.open(io.BytesIO(image_bytes))
            # Convert to RGB if needed (RGBA -> RGB)
            if image.mode in ("RGBA", "LA"):
                background = Image.new("RGB", image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1] if image.mode == "RGBA" else None)
                image = background
            elif image.mode != "RGB":
                image = image.convert("RGB")
        except Exception as e:
            logger.error("Failed to load image: %s", e)
            return OCRText(""), 0.0

        # Run EasyOCR
        try:
            results = self._reader.readtext(
                image, detail=1, paragraph=False, slope_ths=0.3, width_ths=0.5
            )
        except Exception as e:
            logger.error("EasyOCR processing failed: %s", e)
            return OCRText(""), 0.0

        # Extract text and compute avg confidence
        lines = []
        confidences = []
        for (bbox, text, confidence) in results:
            lines.append(text)
            confidences.append(confidence)

        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
        full_text = "\n".join(lines)
        return OCRText(full_text), avg_conf
