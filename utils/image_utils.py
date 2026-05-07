"""
Image Processing Utilities
"""

from PIL import Image

def validate_and_load_image(uploaded_file):
    """Validate and load uploaded image"""
    try:
        image = Image.open(uploaded_file)
        
        # Convert RGBA to RGB if needed
        if image.mode in ('RGBA', 'LA', 'P'):
            rgb_image = Image.new('RGB', image.size, (255, 255, 255))
            r, g, b, a = image.split() if image.mode == 'RGBA' else (None, None, None, None)
            rgb_image.paste(image, mask=a if a else None)
            image = rgb_image
        
        # Resize if too large
        max_dimension = 1024
        if max(image.size) > max_dimension:
            ratio = max_dimension / max(image.size)
            new_size = tuple(int(dim * ratio) for dim in image.size)
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        return image, None
        
    except Exception as e:
        return None, f"Invalid image: {str(e)}"

class ImageProcessor:
    @staticmethod
    def preprocess(image):
        return image
