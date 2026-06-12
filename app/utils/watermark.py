import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

def add_watermark(image_path: str):
    """
    對指定路徑的圖片壓上防篡改浮水印與時間戳記。
    如果檔案不是支援的圖片格式，則不進行處理。
    """
    try:
        # 開啟圖片，確保格式支援
        with Image.open(image_path) as img:
            # 為了能正確畫字且不被 GIF 等索引顏色限制，轉為 RGBA 或 RGB
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
                
            # 建立可繪圖的畫布
            txt_layer = Image.new('RGBA', img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(txt_layer)
            
            # 設定文字內容
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            watermark_text = f"SafeRent 防篡改存證\n{timestamp}"
            
            # 根據圖片大小決定字體大小 (簡單比例計算)
            font_size = max(16, int(img.size[0] / 30))
            
            # 嘗試使用系統字體，如果找不到就用預設字體
            try:
                # Windows 中文常用字體
                font = ImageFont.truetype("msjh.ttc", font_size)
            except IOError:
                try:
                    font = ImageFont.truetype("Arial.ttf", font_size)
                except IOError:
                    font = ImageFont.load_default()
            
            # 計算文字大小以放置在右下角
            # 使用 textbbox 取代舊版的 textsize
            bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 加入一點邊距
            margin = int(font_size * 0.5)
            x = img.size[0] - text_width - margin
            y = img.size[1] - text_height - margin
            
            # 繪製半透明的黑色背景，提升文字可讀性
            bg_bbox = (x - 5, y - 5, x + text_width + 5, y + text_height + 5)
            draw.rectangle(bg_bbox, fill=(0, 0, 0, 128))
            
            # 繪製白色文字
            draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 230))
            
            # 合併原圖與文字圖層
            watermarked = Image.alpha_composite(img, txt_layer)
            
            # 存回原路徑 (為了相容性轉回 RGB 儲存為 JPG 或保留 RGBA 儲存為 PNG)
            # 根據原始副檔名決定儲存方式
            ext = os.path.splitext(image_path)[1].lower()
            if ext in ['.jpg', '.jpeg']:
                watermarked = watermarked.convert('RGB')
                watermarked.save(image_path, format='JPEG', quality=90)
            elif ext == '.png':
                watermarked.save(image_path, format='PNG')
            else:
                # 若為其他格式則預設轉存為 JPEG 或覆蓋
                watermarked = watermarked.convert('RGB')
                watermarked.save(image_path)
                
    except Exception as e:
        # 如果不是圖片或處理失敗，就印出錯誤並保留原檔
        print(f"浮水印處理失敗: {image_path}, 錯誤: {e}")
        pass
