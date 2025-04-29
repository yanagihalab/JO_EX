import requests
import pandas as pd
import time
from tqdm import tqdm

# osmosisのRPCエンドポイント
RPC_URL = "https://osmosis-rpc.polkachu.com"
BLOCK_COUNT = 50000  # 遡るブロック数
MAX_RETRIES = 1000   # 最大リトライ回数
WAIT_TIME = 3        # エラー時の待機時間（秒）

def get_latest_block():
    """最新のブロック番号を取得"""
    url = f"{RPC_URL}/block"
    session = requests.Session()
    for attempt in range(MAX_RETRIES):
        try:
            response = session.get(url, timeout=10)
            if response.status_code == 200:
                return int(response.json()["result"]["block"]["header"]["height"])
            else:
                print(f"[Error] Status Code: {response.status_code}, retrying {attempt+1}/{MAX_RETRIES}...")
        except requests.exceptions.RequestException as e:
            print(f"[Error] {e}, retrying {attempt+1}/{MAX_RETRIES}...")
            time.sleep(WAIT_TIME)
    return None

def get_block(block_height):
    """指定したブロックの情報を取得（リトライ対応）"""
    url = f"{RPC_URL}/block?height={block_height}"
    session = requests.Session()
    for attempt in range(MAX_RETRIES):
        try:
            response = session.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[Error] Status Code: {response.status_code}, retrying {attempt+1}/{MAX_RETRIES}...")
        except requests.exceptions.RequestException as e:
            print(f"[Error] {e}, retrying {attempt+1}/{MAX_RETRIES}...")
            time.sleep(WAIT_TIME)
    return None

# 最新ブロックを取得
LATEST_BLOCK = get_latest_block()
if not LATEST_BLOCK:
    print("最新ブロックの取得に失敗しました。")
    exit(1)

# 取得するブロック範囲
START_BLOCK = LATEST_BLOCK
END_BLOCK = max(START_BLOCK - BLOCK_COUNT, 1)  # 1 より小さくならないように

print(f"最新ブロック: {START_BLOCK}, 取得範囲: {END_BLOCK} 〜 {START_BLOCK}")

# 一時保存用のリスト
block_data = []

# 過去ブロックのデータを取得
previous_proposer = None  # 前のブロックの proposer_address を保存
for height in tqdm(range(END_BLOCK, START_BLOCK + 1), desc="Fetching Blocks", unit="block"):
    block = get_block(height)
    
    if block:
        # 必要な情報を取得
        header = block.get("result", {}).get("block", {}).get("header", {})
        block_info = {
            "height": header.get("height"),  # ブロック番号
            "time": header.get("time"),  # タイムスタンプ（ISO8601形式）
            "proposer_address": header.get("proposer_address"),  # 現在の提案者
            "next_proposer_address": previous_proposer if previous_proposer else "Unknown",  # 1つ前の proposer
            "num_txs": block.get("result", {}).get("block", {}).get("data", {}).get("txs", []),  # トランザクションリスト
        }
        # トランザクション数を取得
        block_info["num_txs"] = len(block_info["num_txs"])
        
        # データをリストに追加
        block_data.append(block_info)

        # 次のブロックの proposer_address のために保存
        previous_proposer = block_info["proposer_address"]
    else:
        print(f"[Warning] Failed to fetch block {height}, skipping.")

    time.sleep(0.5)  # RPCの負荷軽減

# データフレームに変換
df = pd.DataFrame(block_data)

# タイムスタンプをdatetime型に変換
df["time"] = pd.to_datetime(df["time"])

# CSVとして一時保存
df.to_csv("osmo_block_data_temp.csv", index=False)
print("データを 'osmo_block_data_temp.csv' に一時保存しました。")

# 取得データのプレビュー
print(df.head())
