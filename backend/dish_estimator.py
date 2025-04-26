import base64
import mimetypes
import os
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image

load_dotenv()

# --- APIキー設定 ---
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# --- 画像ファイルをbase64に変換 ---
def encode_image(image_data, mime_type=None):
    img = Image.open(image_data)
    # img = Image.open(BytesIO(image_data))
    img_format = img.format
    img.close()

    #MIMEタイプを推測
    mime_type, _ = mimetypes.guess_type(image_data)
    if mime_type is None:
        # 不明な場合は一般的なタイプを設定 (必要に応じて調整)
        if img_format:
            mime_type = f"image/{img_format.lower()}"
        else:
                mime_type = "image/jpeg" # デフォルト
        print(f"警告: MIMEタイプを推測できませんでした。'{mime_type}' を使用します。")

    with open(image_data, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime_type};base64,{encoded}"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "images_for_hackthon")

# 原材料画像ファイル名一覧を ingredient_list に格納
ingredient_list = [
    os.path.splitext(filename)[0]
    for filename in os.listdir(IMAGE_DIR)
    if filename.lower().endswith("png")
]

# --- 画像パスを指定 ---
image_data = os.path.join(BASE_DIR, "test.png")  # 料理画像のパス
base64_image = encode_image(image_data)

# --- Vision APIへのリクエスト（GPT-4V） ---
prompt = f"""この料理画像を見て、まず料理名を推定してください。
次に、この料理に使われていると思われる主要な原材料をできるだけたくさんリストアップしてください。

重要: 原材料は、必ず以下のリストから選択してください。
[{ingredient_list}]

応答形式は以下のようにしてください:
料理名: [ここに料理名]
原材料:
- [原材料1]
- [原材料2]
- [原材料3]
..."""

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url":  { "url": base64_image },
                },
            ],
        }
    ],
    max_tokens=800,
)

# --- 結果を表示 ---
dish_name = response.choices[0].message.content.strip()
print(dish_name)
