import os
import requests
import json
import time
from tqdm import tqdm  # 追加

# 定数定義
BASE_URL_BLOCK = "https://babylon-rpc.publicnode.com/block"
BASE_URL_VALIDATORS = "https://babylon-rpc.publicnode.com/validators"
PER_PAGE = 100
TOTAL_PAGES = 1
RETRY_LIMIT = 100
SLEEP_TIME = 1
BLOCK_COUNT = 500
SAVE_DIR = "current"

# 保存先ディレクトリの作成（存在しない場合）
os.makedirs(SAVE_DIR, exist_ok=True)

headers = {"User-Agent": "Mozilla/5.0"}

# 最新のブロック番号を取得
def get_latest_height():
    response = requests.get(BASE_URL_BLOCK, headers=headers, timeout=10)
    response.raise_for_status()
    latest_block = response.json()
    return int(latest_block["result"]["block"]["header"]["height"])

latest_height = get_latest_height()
print(f"最新のブロック番号: {latest_height}")

# 最新のブロックから5000ブロック分さかのぼって取得
for i in tqdm(range(BLOCK_COUNT), desc="Fetching blocks", unit="block"):
    height = latest_height - i

    # ---- 1. ブロック情報の取得 ----
    block_info = {}
    try:
        block_url = f"{BASE_URL_BLOCK}?height={height}"
        block_response = requests.get(block_url, headers=headers, timeout=10)
        block_response.raise_for_status()
        block_info = block_response.json().get("result", {})
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Failed to fetch block info for height {height}: {e}")

    # ---- 2. バリデータ情報の取得 ----
    block_validators = []

    for page in range(1, TOTAL_PAGES + 1):
        url = f"{BASE_URL_VALIDATORS}?height={height}&per_page={PER_PAGE}&page={page}"
        retries = 0

        while retries < RETRY_LIMIT:
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()

                data = response.json()
                result = data.get("result")

                if not result or not isinstance(result, dict) or "validators" not in result:
                    break

                validators = result["validators"]

                if not validators:
                    break

                block_validators.extend(validators)
                break

            except requests.exceptions.RequestException as e:
                retries += 1
                time.sleep(SLEEP_TIME)

        if retries == RETRY_LIMIT:
            print(f"  ❗ Failed to fetch page {page} after {RETRY_LIMIT} attempts. Skipping.")

    # ---- 3. JSONファイルとして保存 ----
    if block_info or block_validators:
        output = {
            "block_info": block_info,
            "validators": block_validators
        }
        filename = os.path.join(SAVE_DIR, f"BlockNum_{height}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
    else:
        print(f"⚠️ No data found for height {height}. Skipping file creation.")
