import os
import json
import pandas as pd
from tqdm import tqdm
from collections import defaultdict
from datetime import datetime

# === ディレクトリ設定 ===
TARGET_DIR = "./current"
SUMMARY_DIR = "./analysis_results"
VALIDATOR_DIR = "./output"
os.makedirs(SUMMARY_DIR, exist_ok=True)
os.makedirs(VALIDATOR_DIR, exist_ok=True)

# ブロック数制限を設定
MAX_BLOCKS = 50000
block_counter = 0

def parse_timestamp(ts: str) -> datetime | None:
    if ts.startswith("0001-01-01"):
        return None
    if ts.endswith("Z"):
        ts = ts[:-1]
    if '.' in ts:
        date_part, frac = ts.split('.')
        frac = (frac + '000000')[:6]
        ts = f"{date_part}.{frac}"
    return datetime.fromisoformat(ts)

# データ収集
validator_sign_counts = defaultdict(int)
validator_sign_timestamps = defaultdict(list)
validator_delay_values = defaultdict(list)
all_validators_set = set()
all_block_heights = set()
block_data = []

# メイン処理
for filename in tqdm(sorted(os.listdir(TARGET_DIR))):
    if block_counter >= MAX_BLOCKS:
        print(f"\n⚠️ {MAX_BLOCKS}ブロックに到達しました。処理を終了します。")
        break

    if not filename.endswith(".json"):
        continue

    path = os.path.join(TARGET_DIR, filename)

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if 'block_info' not in data or 'block' not in data['block_info']:
            continue

        block = data['block_info']['block']
        height = int(block['header']['height'])
        block_time = parse_timestamp(block['header']['time'])
        all_block_heights.add(height)

        sigs = block['last_commit']['signatures']
        timestamps = []
        delays_from_block = []

        for s in sigs:
            addr = s.get('validator_address')
            ts = s.get('timestamp')
            sig_time = parse_timestamp(ts)

            if addr:
                validator_sign_counts[addr] += 1
                all_validators_set.add(addr)

            if sig_time and addr:
                validator_sign_timestamps[addr].append({
                    "block_height": height,
                    "timestamp": ts
                })

                if block_time:
                    delay_sec = abs((sig_time - block_time).total_seconds())
                    delays_from_block.append(delay_sec)
                    validator_delay_values[addr].append((height, delay_sec))

                timestamps.append(sig_time)

        signature_diff_sec = max(delays_from_block) if delays_from_block else 0
        signature_spread_sec = (max(timestamps) - min(timestamps)).total_seconds() if len(timestamps) >= 2 else 0

        block_data.append({
            "block_height": height,
            "block_time": block_time,
            "signature_diff_sec": signature_diff_sec,
            "signature_spread_sec": signature_spread_sec
        })

        block_counter += 1

    except Exception as e:
        print(f"⚠️ Error in {filename}: {e}")

# DataFrame化
df_blocks = pd.DataFrame(block_data)
df_blocks.sort_values("block_height", inplace=True)
df_blocks["block_interval_sec"] = df_blocks["block_time"].diff().dt.total_seconds()
df_blocks.dropna(inplace=True)

# 01. バリデータ署名率
total_blocks = len(all_block_heights)
df_signrate = pd.DataFrame([
    {
        "validator_address": addr,
        "signed_blocks": validator_sign_counts.get(addr, 0),
        "total_blocks": total_blocks,
        "signature_rate_percent": round(validator_sign_counts.get(addr, 0) / total_blocks * 100, 2)
    }
    for addr in sorted(all_validators_set)
])
df_signrate.sort_values("signature_rate_percent", ascending=False, inplace=True)
df_signrate.to_csv(os.path.join(SUMMARY_DIR, "01_validator_signature_rates.csv"), index=False)

# 02. ブロック内署名ばらつき（spread）
df_blocks[["block_height", "signature_spread_sec"]].to_csv(
    os.path.join(SUMMARY_DIR, "02_block_signature_spread.csv"), index=False)

# 03. ブロック間隔と最大署名遅延
df_blocks[["block_height", "block_interval_sec", "signature_diff_sec"]].to_csv(
    os.path.join(SUMMARY_DIR, "03_block_vs_signature_delay.csv"), index=False)

# 04. 遅延ランキング（最大・平均遅延 + ブロック）
delay_stats = []
for addr, delay_list in validator_delay_values.items():
    max_block, max_delay = max(delay_list, key=lambda x: x[1])
    avg_delay = sum(d for _, d in delay_list) / len(delay_list)
    delay_stats.append({
        "validator_address": addr,
        "max_delay_sec": round(max_delay, 3),
        "avg_delay_sec": round(avg_delay, 3),
        "signed_blocks": len(delay_list),
        "max_delay_block_height": max_block
    })
df_delays = pd.DataFrame(delay_stats)
df_delays.sort_values("avg_delay_sec", ascending=False, inplace=True)
df_delays.to_csv(os.path.join(SUMMARY_DIR, "04_validator_signature_delays.csv"), index=False)

# 05. 各バリデータの署名履歴（outputフォルダに個別保存）
for addr, records in validator_sign_timestamps.items():
    df = pd.DataFrame(records)
    df.sort_values("block_height", inplace=True)
    output_file = os.path.join(VALIDATOR_DIR, f"{addr}.csv")
    df.to_csv(output_file, index=False)

# 完了ログ
print("\n✅ 出力完了！")
print(f"📂 集計ファイル: {SUMMARY_DIR}/")
print(f"📂 バリデータ署名履歴: {VALIDATOR_DIR}/")
