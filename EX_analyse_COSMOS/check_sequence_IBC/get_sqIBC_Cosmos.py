import requests
import time
import pandas as pd
from datetime import datetime, timedelta
import tqdm
import os

# RPCエンドポイント
RPC_URL = "https://cosmos-rpc.publicnode.com/block_results?height="
BLOCK_HEADER_URL = "https://cosmos-rpc.publicnode.com/block?height="

# ディレクトリ設定
TEMP_DIR = "current"
FINAL_DIR = "."
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(FINAL_DIR, exist_ok=True)

# 共通関数定義
def fetch_json(url, timeout=5):
    while True:
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                return response.json()
            print(f"Failed to fetch {url}, retrying...")
        except Exception as e:
            print(f"Error fetching {url}, retrying: {e}")
        time.sleep(3)

# 任意の取得時間（時間単位で設定可能）
HOURS_TO_COLLECT = 12
INTERVAL_HOURS = 20

# 最新ブロックの高さと時刻を取得
def get_latest_block_height_and_time():
    status_url = "https://cosmos-rpc.publicnode.com/status"
    data = fetch_json(status_url)
    latest_height = int(data["result"]["sync_info"]["latest_block_height"])
    latest_time_raw = data["result"]["sync_info"]["latest_block_time"]

    latest_time = latest_time_raw.replace("Z", "")
    if "." in latest_time:
        base_time, fraction = latest_time.split(".")
        fraction = fraction.ljust(6, "0")[:6]
        latest_time = f"{base_time}.{fraction}"
    latest_time = datetime.fromisoformat(latest_time)

    return latest_height, latest_time

# 開始ブロックと時間範囲を決定
START_HEIGHT, START_TIME = get_latest_block_height_and_time()
END_TIME = START_TIME - timedelta(hours=HOURS_TO_COLLECT)
NEXT_SAVE_TIME = START_TIME - timedelta(hours=INTERVAL_HOURS)

print(f"Analyzing from latest block {START_HEIGHT} back {HOURS_TO_COLLECT} hours (until {END_TIME})")

send_packets = {}
ack_packets = {}
recv_packets = []
block_timestamps = {}
fee_data = {}

def fetch_block_timestamp(height):
    data = fetch_json(BLOCK_HEADER_URL + str(height))
    if data:
        timestamp = data.get("result", {}).get("block", {}).get("header", {}).get("time", None)
        if timestamp:
            timestamp = timestamp.replace("Z", "")
            if "." in timestamp:
                base_time, fraction = timestamp.split(".")
                fraction = fraction.ljust(6, "0")[:6]
                timestamp = f"{base_time}.{fraction}"
            try:
                return datetime.fromisoformat(timestamp)
            except ValueError:
                print(f"Invalid ISO format: {timestamp}")
    return None

def parse_ibc_events(height, block_data):
    if not block_data:
        print(f"Warning: Block data is invalid for height {height}")
        return

    events = block_data.get("begin_block_events", []) + block_data.get("end_block_events", [])
    tx_fees = {}

    for tx in block_data.get("txs_results", []) or []:
        tx_hash = tx.get("hash", "unknown")
        events.extend(tx.get("events", []))

        fee_amount = None
        fee_denom = None
        for event in events:
            if event.get("type") in ["tx_fee", "fee_pay"]:
                for attr in event.get("attributes", []):
                    if attr.get("key") in ["amount", "fee"]:
                        fee_amount = attr.get("value")
                    elif attr.get("key") == "denom":
                        fee_denom = attr.get("value")
                tx_fees[tx_hash] = {"fee_amount": fee_amount, "fee_denom": fee_denom}

        for event in events:
            if event.get("type") in ["send_packet", "acknowledge_packet", "recv_packet"]:
                packet_data = {attr.get("key"): attr.get("value") for attr in event.get("attributes", [])}
                sequence, channel_id = packet_data.get("packet_sequence"), packet_data.get("packet_src_channel")
                if sequence and channel_id:
                    key = (channel_id, sequence)
                    if event["type"] == "send_packet":
                        send_packets[key] = height
                        fee_data[key] = tx_fees.get(tx_hash, {"fee_amount": None, "fee_denom": None})
                    elif event["type"] == "acknowledge_packet":
                        ack_packets[key] = height
                    elif event["type"] == "recv_packet":
                        fee = tx_fees.get(tx_hash, {"fee_amount": None, "fee_denom": None})
                        recv_packets.append({
                            "channel_id": channel_id,
                            "sequence": sequence,
                            "recv_height": height,
                            "recv_time": block_timestamps.get(height).isoformat() if height in block_timestamps else None,
                            "fee_amount": fee.get("fee_amount"),
                            "fee_denom": fee.get("fee_denom"),
                            "source_port": packet_data.get("packet_src_port"),
                            "destination_channel": packet_data.get("packet_dst_channel"),
                            "timeout_height": packet_data.get("packet_timeout_height")
                        })

def save_csv(start_height, end_height, directory):
    packet_delays = [
        {
            "channel_id": key[0],
            "sequence": key[1],
            "send_height": send_packets[key],
            "send_time": block_timestamps.get(send_packets[key]).isoformat() if send_packets.get(key) in block_timestamps else None,
            "ack_height": ack_packets.get(key),
            "ack_time": block_timestamps.get(ack_packets[key]).isoformat() if ack_packets.get(key) in block_timestamps else None,
            "block_delay": ack_packets.get(key, 0) - send_packets[key] if ack_packets.get(key) else None,
            "fee_amount": fee_data.get(key, {}).get("fee_amount"),
            "fee_denom": fee_data.get(key, {}).get("fee_denom")
        }
        for key in send_packets.keys()
    ]

    if packet_delays:
        df = pd.DataFrame(packet_delays)
        csv_filename = os.path.join(directory, f"GG_COSMO_ibc_sq_pk_{start_height}-{end_height}.csv")
        df.to_csv(csv_filename, index=False)
        print(f"CSV file saved: {csv_filename}")

    if recv_packets:
        df_recv = pd.DataFrame(recv_packets)
        recv_filename = os.path.join(directory, f"GG_COSMO_ibc_sq_rv_{start_height}-{end_height}.csv")
        df_recv.to_csv(recv_filename, index=False)
        print(f"Recv packet CSV file saved: {recv_filename}")

# メイン処理
start_time = time.time()
current_height = START_HEIGHT
with tqdm.tqdm(desc="Processing Blocks") as pbar:
    while True:
        block_time = fetch_block_timestamp(current_height)
        if block_time is None:
            print(f"Skipping block {current_height} due to missing timestamp.")
            current_height -= 1
            continue

        block_timestamps[current_height] = block_time

        if block_time <= END_TIME:
            break

        block_results = fetch_json(RPC_URL + str(current_height))
        if block_results:
            parse_ibc_events(current_height, block_results.get("result", {}))

        elapsed_time = time.time() - start_time
        processed_blocks = START_HEIGHT - current_height + 1
        avg_time_per_block = elapsed_time / processed_blocks
        pbar.set_postfix({"ETA": str(timedelta(seconds=int(avg_time_per_block * 1000)))})
        pbar.update(1)

        if block_time <= NEXT_SAVE_TIME:
            save_csv(current_height, START_HEIGHT, TEMP_DIR)
            START_HEIGHT = current_height
            NEXT_SAVE_TIME -= timedelta(hours=INTERVAL_HOURS)

        current_height -= 1
        time.sleep(0.1)

save_csv(current_height + 1, START_HEIGHT, FINAL_DIR)
print("Final CSV file saved successfully.")
