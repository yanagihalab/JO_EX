import requests
import json
import time

BASE_URL = "https://cosmos-rpc.publicnode.com/validators"
START_HEIGHT = 25066094  # 取得開始ブロック
BLOCK_COUNT = 5000  # 取得するブロック数
PER_PAGE = 100  # 1ページの取得件数
TOTAL_PAGES = 2  # 取得するページ数
RETRY_LIMIT = 100  # 最大再試行回数

headers = {
    "User-Agent": "Mozilla/5.0",
}

for i in range(BLOCK_COUNT):
    height = START_HEIGHT + i  # ブロックの高さ
    print(f"\n🔍 {i+1}/{BLOCK_COUNT} - Fetching data for block height: {height}")

    block_validators = []  # 1つのブロックのデータを保存するリスト

    for page in range(1, TOTAL_PAGES + 1):
        url = f"{BASE_URL}?height={height}&per_page={PER_PAGE}&page={page}"
        retries = 0

        while retries < RETRY_LIMIT:
            try:
                print(f"  📡 Fetching page {page}...")
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()  # HTTPエラーがあれば例外を発生

                data = response.json()
                
                result = data.get("result", [])

                if not result:
                    print(f"  ⚠️ No data returned for height {height}, page {page}. Skipping.")
                    break  # 空のレスポンスなら次のページへ

                block_validators.append(data['result'])  # データをリストに追加
                print(block_validators)
                print(f"  ✅ Success! {len(result)} records added.")
                break  # 正常取得できたのでループを抜ける

            except requests.exceptions.RequestException as e:
                retries += 1
                print(f"  ❌ Error fetching page {page}. Retrying {retries}/{RETRY_LIMIT}...")
        t=1
        print("sleep time is", t)
        time.sleep(t)

        if retries == RETRY_LIMIT:
            print(f"  ❗ Failed to fetch page {page} after {RETRY_LIMIT} attempts. Skipping.")

    # 取得したデータをブロックごとに保存
    if block_validators:
        filename = f"current/validators_{height}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(block_validators, f, indent=4, ensure_ascii=False)
        print(f"✅ 保存完了: {filename} ({len(block_validators)} 件)")

    else:
        print(f"⚠️ No data found for height {height}. Skipping file creation.")
