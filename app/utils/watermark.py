import os
from PIL import Image, ImageDraw, ImageFont

def add_watermark(input_path, output_path, text="僅供租屋平台審核使用"):
    """
    Add a diagonal watermark to the image.
    """
    try:
        # Open the original image
        with Image.open(input_path) as img:
            img = img.convert("RGBA")
            
            # Make a blank image for the text, initialized to transparent text color
            txt = Image.new('RGBA', img.size, (255,255,255,0))
            
            # Get a font
            try:
                # Try to load a generic TTF font (Windows usually has arial or msgothic)
                font = ImageFont.truetype("arial.ttf", size=min(img.size)//15)
            except IOError:
                # Fallback to default font if arial is not available
                font = ImageFont.load_default()
            
            # Get drawing context
            d = ImageDraw.Draw(txt)
            
            # Determine text size (this approach works for modern Pillow)
            text_bbox = d.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            # Center of the image
            x = (img.size[0] - text_width) / 2
            y = (img.size[1] - text_height) / 2
            
            # Draw text, half opacity
            d.text((x, y), text, font=font, fill=(255,0,0,128))
            
            # Combine
            watermarked = Image.alpha_composite(img, txt)
            
            # Save back as RGB (to support saving as JPEG if needed)
            watermarked = watermarked.convert("RGB")
            watermarked.save(output_path)
            return True
    except Exception as e:
        print(f"Failed to add watermark: {e}")
        return False
