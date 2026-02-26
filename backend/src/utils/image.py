import base64
import io

from PIL import Image, UnidentifiedImageError


class ImageProcessor:
    def __init__(self, max_dimension: int = 1024, max_size_mb: int = 5):
        self.max_dimension = max_dimension
        self.max_size_mb = max_size_mb

    def process(self, image_bytes: bytes) -> str:
        """
        Validates, Resizes, and Re-encodes raw bytes into a clean Base64 string.
        """
        # 1. Size Check (Fast fail)
        if len(image_bytes) > (self.max_size_mb * 1024 * 1024):
            raise ValueError(f"Image too large. Max size is {self.max_size_mb}MB.")

        try:
            # 2. Magic Bytes Check (Security)
            # Opening with PIL automatically checks the file header/structure
            with io.BytesIO(image_bytes) as buf:
                with Image.open(buf) as img:
                    img.verify()  # This fails if the bytes aren't a valid image format

                    if not img.format or img.format.upper() not in [
                        "PNG",
                        "JPEG",
                        "WEBP",
                    ]:
                        raise ValueError(f"Unsupported image format: {img.format}")

            # 3. Resize Logic
            # We must re-open because img.verify() consumes the file pointer
            img = Image.open(io.BytesIO(image_bytes))

            # Force RGB (Fixes transparency issues when saving as JPEG)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            width, height = img.size

            # Only process if resizing is actually needed
            if width > self.max_dimension or height > self.max_dimension:
                img.thumbnail(
                    (self.max_dimension, self.max_dimension), Image.Resampling.LANCZOS
                )

                # Save to buffer as optimized JPEG
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=85)
                image_bytes = buffer.getvalue()

            # 4. Return Data URI String

            mime_type = "image/jpeg"
            if img.format:
                mime_type = f"image/{img.format.lower()}"

            b64_str = base64.b64encode(image_bytes).decode("utf-8")
            return f"data:{mime_type};base64,{b64_str}"

        except (UnidentifiedImageError, ValueError):
            raise ValueError("Invalid or corrupt image data.")
        except Exception as e:
            raise ValueError(f"Image processing failed: {str(e)}")
