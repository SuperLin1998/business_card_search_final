from google.cloud import vision
import io

def extract_text(image_path):
    """使用 Google Vision API 辨識繁體中文名片文字"""

    # 建立 Vision API 客戶端
    client = vision.ImageAnnotatorClient()

    # 讀取本地圖片檔案
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    # 設定語言提示：繁體中文
    image_context = vision.ImageContext(
        language_hints=["zh-TW"]
    )

    # 呼叫文字偵測 API
    response = client.text_detection(image=image, image_context=image_context)

    texts = response.text_annotations

    # 回傳辨識結果
    if texts:
        return texts[0].description.strip()  # 第一筆是整張圖的完整辨識結果
    else:
        return "未偵測到任何文字。"
