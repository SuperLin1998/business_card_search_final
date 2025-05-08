import io
import json
from google.cloud import vision
from google.cloud import secretmanager
from google.oauth2 import service_account

def create_vision_client_from_secret(secret_id: str, project_id: str, version_id: str = "latest"):
    # 從 GCP Secret Manager 取得 JSON 金鑰字串
    client = secretmanager.SecretManagerServiceClient()
    secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(name=secret_name)

    service_account_info = json.loads(response.payload.data.decode("UTF-8"))
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    vision_client = vision.ImageAnnotatorClient(credentials=credentials)
    return vision_client

def extract_text(image_path):
    vision_client = create_vision_client_from_secret(
        secret_id="business_card_search_finally_json",
        project_id="135408477080"
    )

    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    image_context = vision.ImageContext(language_hints=["zh-TW"])
    response = vision_client.text_detection(image=image, image_context=image_context)
    texts = response.text_annotations

    if texts:
        return texts[0].description.strip()
    else:
        return "未偵測到任何文字。"
