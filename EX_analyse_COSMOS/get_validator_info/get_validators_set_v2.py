import os
import requests
import json
import time

# 定数定義
BASE_URL_BLOCK = "https://cosmos-rpc.publicnode.com/block"
BASE_URL_VALIDATORS = "https://cosmos-rpc.publicnode.com/validators"
START_HEIGHT = 25176281
BLOCK_COUNT = 40000
PER_PAGE = 100
TOTAL_PAGES = 2
RETRY_LIMIT = 100
SLEEP_TIME = 1
SAVE_DIR = "current"

# 保存先ディレクトリの作成（存在しない場合）
os.makedirs(SAVE_DIR, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0",
}

for i in range(BLOCK_COUNT):
    height = START_HEIGHT + i
    print(f"\n🔍 {i+1}/{BLOCK_COUNT} - Fetching data for block height: {height}")

    # ---- 1. ブロック情報の取得 ----
    block_info = {}
    try:
        block_url = f"{BASE_URL_BLOCK}?height={height}"
        print(f"  🧱 Fetching block info: {block_url}")
        block_response = requests.get(block_url, headers=headers, timeout=10)
        block_response.raise_for_status()
        block_info = block_response.json().get("result", {})
        print("  ✅ Block info fetched.")
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Failed to fetch block info for height {height}: {e}")

    # ---- 2. バリデータ情報の取得 ----
    block_validators = []

    for page in range(1, TOTAL_PAGES + 1):
        url = f"{BASE_URL_VALIDATORS}?height={height}&per_page={PER_PAGE}&page={page}"
        retries = 0

        while retries < RETRY_LIMIT:
            try:
                print(f"  📡 Fetching validators page {page}...")
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()

                data = response.json()
                result = data.get("result")

                if not result or not isinstance(result, dict) or "validators" not in result:
                    print(f"  ⚠️ No valid 'validators' data for height {height}, page {page}. Skipping.")
                    break

                validators = result["validators"]
                block_validators.extend(validators)
                print(f"  ✅ Success! {len(validators)} records added.")
                break

            except requests.exceptions.RequestException as e:
                retries += 1
                print(f"  ❌ Error fetching page {page}. Retrying {retries}/{RETRY_LIMIT}...")
                time.sleep(SLEEP_TIME)

        if retries == RETRY_LIMIT:
            print(f"  ❗ Failed to fetch page {page} after {RETRY_LIMIT} attempts. Skipping.")

    # ---- 3. JSONファイルとして保存 ----
    if block_info or block_validators:
        output = {
            "block_info": block_info,
            "validators": block_validators
        }
        filename = os.path.join(SAVE_DIR, f"validators_{height}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
        print(f"✅ 保存完了: {filename} ({len(block_validators)} validators)")
    else:
        print(f"⚠️ No data found for height {height}. Skipping file creation.")
