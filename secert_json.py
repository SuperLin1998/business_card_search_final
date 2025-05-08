import os
import tempfile
from google.cloud import secretmanager, vision
import base64
from PIL import Image
import io

def test_vision_with_secret():
    try:
        # 初始化 Secret Manager 客戶端
        sm_client = secretmanager.SecretManagerServiceClient()
        
        # 設定 Secret 路徑 (使用您的 Secret ID)
        project_id = "mysqlproject20250503"  # 替換為您的專案 ID
        secret_id = "visionapikey20250508"  # 您的 Secret ID
        version_id = "latest"
        
        secret_path = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        print(f"正在訪問 Secret: {secret_path}")
        
        # 訪問 Secret 內容
        response = sm_client.access_secret_version(name=secret_path)
        secret_payload = response.payload.data.decode('UTF-8')
        
        # 將 Secret 寫入臨時檔案
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            temp_file.write(secret_payload)
            credentials_path = temp_file.name
        
        print(f"憑證已寫入臨時檔案: {credentials_path}")
        
        # 設定憑證環境變數
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        
        # 初始化 Vision API 客戶端
        vision_client = vision.ImageAnnotatorClient()
        print("已初始化 Vision API 客戶端")
        
        # 建立測試圖片 (或使用現有圖片)
        # 這裡建立一個簡單的純色圖片作為測試
        test_image = Image.new('RGB', (100, 100), color='red')
        img_byte_arr = io.BytesIO()
        test_image.save(img_byte_arr, format='JPEG')
        img_content = img_byte_arr.getvalue()
        
        # 調用 Vision API
        vision_image = vision.Image(content=img_content)
        response = vision_client.label_detection(image=vision_image)
        
        # 輸出結果
        print("\n=== 測試結果 ===")
        print(f"API 回應狀態: {response.error.message if response.error.message else '成功'}")
        
        if response.label_annotations:
            print("檢測到的標籤:")
            for label in response.label_annotations:
                print(f"  - {label.description} (可信度: {label.score:.2f})")
        else:
            print("未檢測到標籤")
        
        # 清理臨時檔案
        os.unlink(credentials_path)
        return True, "測試成功完成"
        
    except Exception as e:
        print(f"測試失敗: {str(e)}")
        # 確保清理臨時檔案
        if 'credentials_path' in locals() and os.path.exists(credentials_path):
            os.unlink(credentials_path)
        return False, str(e)

# 執行測試
success, message = test_vision_with_secret()
print(f"\n總結: {'✅ 測試通過' if success else '❌ 測試失敗'}")
print(f"訊息: {message}")