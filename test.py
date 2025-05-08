import os
from google.cloud import secretmanager
from google.cloud import vision
from google.oauth2 import service_account
import io

def test_secret_and_vision(project_id: str, secret_id: str, version_id: str = "latest"):
    print("▶ 測試：從 Secret Manager 讀取金鑰並初始化 Vision Client")

    # 建立 Secret Manager 客戶端
    sm_client = secretmanager.SecretManagerServiceClient()

    # 構建 Secret 名稱
    secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # 存取 Secret
    response = sm_client.access_secret_version(name=secret_name)
    secret_payload = response.payload.data.decode("UTF-8")

    # 將 JSON 憑證字串轉成憑證物件
    credentials = service_account.Credentials.from_service_account_info(eval(secret_payload))

    # 初始化 Vision API 客戶端
    vision_client = vision.ImageAnnotatorClient(credentials=credentials)

    # 使用 Vision API 偵測圖像文字（這裡以 test_image.jpg 為例）
    image_path = "a776445e-4a24-4fb8-b014-93f555515f7c.jpg"
    if not os.path.exists(image_path):
        print(f"⚠ 測試圖片不存在：{image_path}")
        return

    with io.open(image_path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = vision_client.text_detection(image=image)

    texts = response.text_annotations
    if texts:
        print("✅ 成功辨識文字：")
        for text in texts:
            print(f"- {text.description}")
    else:
        print("⚠ 沒有辨識到任何文字")

    if response.error.message:
        raise Exception(f"Vision API 錯誤：{response.error.message}")

if __name__ == "__main__":
    test_secret_and_vision(
        project_id="135408477080",
        secret_id="business_card_search_finally_json"
    )
