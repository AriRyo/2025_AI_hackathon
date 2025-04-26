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
import base64
import mimetypes
import os
import re
from io import BytesIO

from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image

load_dotenv()

# --- APIキー設定 ---
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# --- 原材料画像ファイル名一覧をリストに格納 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "images_for_hackthon")

ingredient_list = [
    os.path.splitext(filename)[0]
    for filename in os.listdir(IMAGE_DIR)
    if filename.lower().endswith("png")
]

# --- 画像ファイルをbase64に変換 ---
def encode_image(image_data, mime_type=None):
    #テスト用 -> 後でコメントアウト
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

# --- 料理名と原材料を推定 ---
def estimate_dish(image_data: bytes):
    # 画像パスを指定
    # image_data = os.path.join(BASE_DIR, "test.png")  # 料理画像のパス
    base64_image = encode_image(image_data)

    prompt2 = (
        "この料理画像を見て、まず料理名を推定してください。\n"
        "次に、この料理に一般的に使われる原材料をできるだけたくさんリストアップしてください。\n"
        "調味料は不要です。\n"

        "応答形式は以下のようにしてください:\n"
        "料理名: [ここに料理名]\n"
        "原材料:\n"
        "- [原材料1]\n"
        "- [原材料2]\n"
        "- [原材料3]\n"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt2
                    },
                    {
                        "type": "image_url",
                        "image_url":  { "url": base64_image },
                    },
                ],
            }
        ],
        max_tokens=800,
        temperature = 0.1
    )

    # --- 結果を表示 ---
    dish_name = response.choices[0].message.content.strip()
    return dish_name

# --- 新しく定義する原材料抽出関数 ---
def extract_ingredients_from_response(response_text: str) -> list[str]:
    if not response_text:
        return []

    # "原材料:" のセクションを探す (大文字小文字無視、改行も含む)
    match_section = re.search(r"原材料:(.*)", response_text, re.IGNORECASE | re.DOTALL)

    if match_section:
        # "原材料:" より後のテキスト部分を取得
        ingredient_text_block = match_section.group(1).strip()

        # 箇条書き("- " または "-") で始まる行から原材料名を抽出
        found_items = re.findall(r"^\s*-\s*(.+)", ingredient_text_block, re.MULTILINE)
        ingredients = [item.strip() for item in found_items]

    return ingredients

def filter_ingredients_with_ai(
    ai_extracted_ingredients: list[str], # 1回目のAIが抽出したリスト
    allowed_ingredients: list[str],      # 許可リスト (ingredient_list)
    ) -> list[str]:
    if not ai_extracted_ingredients:
        return [] # 元のリストが空なら空リストを返す

    allowed_ingredients_str = ", ".join(allowed_ingredients)
    ai_ingredients_str = "\n".join([f"- {item}" for item in ai_extracted_ingredients])

    prompt = f"""以下の「抽出された原材料リスト」にある各項目について、下記の「許可された原材料リスト」に含まれる項目と実質的に同じものを指しているか判定してください。(例: 「豚肉(薄切り)」は「pork」と一致、「玉ねぎ」は「onion」と一致)
    判定の結果、一致すると判断された「許可された原材料リスト」中の項目名だけを、カンマ区切りで一行で出力してください。重複は含めないでください。リスト中のどの項目とも一致しない抽出項目は無視してください。料理名や説明、「原材料:」などの接頭辞は不要です。許可リスト中の原材料名だけをカンマ区切りで出力してください。

    抽出された原材料リスト:
    {ai_ingredients_str}

    許可された原材料リスト:
    [{allowed_ingredients_str}]

    出力例: 豚肉, ピーマン, 玉ねぎ
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=len(allowed_ingredients) * 10, # 応答に必要なトークン数を考慮
        temperature=0.1
    )

    filtered_result_text = response.choices[0].message.content.strip()
    print(f"フィルタリングAIの応答: {filtered_result_text}")

    # カンマ区切りの応答をパースしてリストにする
    # 空白や空要素を除去
    final_ingredients = [
        item.strip() for item in filtered_result_text.split(',')
        if item.strip() and item.strip() in allowed_ingredients # 念のため許可リストに含まれるか再確認
    ]
    return sorted(list(set(final_ingredients))) # 重複除去してソート

image_data = os.path.join(BASE_DIR, "test.png")
res = estimate_dish(image_data)
ingre = extract_ingredients_from_response(res)
a = filter_ingredients_with_ai(ingre, ingredient_list)
