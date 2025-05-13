import json
import os
from collections import Counter
import pandas as pd

MAX_BLOCKS = 30000


def analyze_block_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = {}
    header = data["block_info"]["block"]["header"]
    result["file"] = os.path.basename(file_path)
    result["height"] = int(header["height"])
    result["timestamp"] = header["time"]
    result["chain_id"] = header.get("chain_id", "N/A")
    result["proposer_address"] = header.get("proposer_address", "N/A")
    result["validators"] = data.get("validators", [])

    txs = data["block_info"]["block"]["data"].get("txs", [])
    result["num_transactions"] = len(txs)

    signatures = data["block_info"]["block"]["last_commit"].get("signatures", [])
    result["num_signatures"] = len(signatures)

    validators = result["validators"]
    addresses = [v["address"] for v in validators]
    voting_powers = [int(v["voting_power"]) for v in validators]
    proposer_priorities = [int(v["proposer_priority"]) for v in validators]

    result["num_validators"] = len(validators)
    result["unique_validator_addresses"] = len(set(addresses))
    result["max_voting_power"] = max(voting_powers) if voting_powers else 0
    result["min_voting_power"] = min(voting_powers) if voting_powers else 0
    result["total_voting_power"] = sum(voting_powers)

    if proposer_priorities:
        max_priority = max(proposer_priorities)
        max_index = proposer_priorities.index(max_priority)
        max_address = addresses[max_index]
        result["max_proposer_priority"] = max_priority
        result["max_priority_address"] = max_address
        result["matches_max_priority"] = (result["proposer_address"] == max_address)

        min_priority = min(proposer_priorities)
        min_index = proposer_priorities.index(min_priority)
        min_address = addresses[min_index]
        result["min_proposer_priority"] = min_priority
        result["min_priority_address"] = min_address
        result["matches_min_priority"] = (result["proposer_address"] == min_address)
    else:
        result["max_proposer_priority"] = None
        result["max_priority_address"] = None
        result["matches_max_priority"] = False
        result["min_proposer_priority"] = None
        result["min_priority_address"] = None
        result["matches_min_priority"] = False

    return result


def analyze_all_blocks(directory):
    results = []
    block_counter = 0
    for filename in sorted(os.listdir(directory)):
        if block_counter >= MAX_BLOCKS:
            print(f"⚠️ {MAX_BLOCKS}ブロックに到達しました。処理を終了します。")
            break

        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            try:
                analysis = analyze_block_json(file_path)
                results.append(analysis)
                block_counter += 1
            except Exception as e:
                print(f"⚠️ Failed to analyze {filename}: {e}")
    return results


data_directory = "./current"

if __name__ == "__main__":
    all_results = analyze_all_blocks(data_directory)

    for i in range(1, len(all_results)):
        prev = all_results[i - 1]
        curr = all_results[i]
        curr["matches_prev_max_priority"] = (
            curr["proposer_address"] == prev.get("max_priority_address")
        )
    if all_results:
        all_results[0]["matches_prev_max_priority"] = None

    rank_counter = Counter()
    for i in range(1, len(all_results)):
        prev = all_results[i - 1]
        curr = all_results[i]

        if not curr.get("matches_prev_max_priority"):
            proposer = curr["proposer_address"]
            prev_validators = prev.get("validators", [])
            if prev_validators:
                sorted_validators = sorted(
                    prev_validators,
                    key=lambda v: int(v["proposer_priority"]),
                    reverse=True
                )
                for rank, val in enumerate(sorted_validators, start=1):
                    if val["address"] == proposer:
                        rank_counter[rank] += 1
                        curr["proposer_rank_in_prev"] = rank
                        break
                else:
                    rank_counter["not_found"] += 1
                    curr["proposer_rank_in_prev"] = None
            else:
                curr["proposer_rank_in_prev"] = None
        else:
            curr["proposer_rank_in_prev"] = 1

    total = len(all_results)
    match_min = sum(1 for r in all_results if r.get("matches_min_priority"))
    match_prev = sum(1 for r in all_results[1:] if r.get("matches_prev_max_priority"))
    rate_min = (match_min / total * 100) if total else 0
    rate_prev = (match_prev / (total - 1) * 100) if total > 1 else 0

    print(f"\n✅ Matches MIN:       {match_min} / {total} blocks ({rate_min:.2f}%)")
    print(f"✅ Matches PREV MAX:  {match_prev} / {total - 1} blocks ({rate_prev:.2f}%)")

    print("\n📊 Rank of proposer in previous block (when mismatched):")
    for rank, count in sorted(rank_counter.items()):
        print(f"  Rank {rank}: {count} blocks")

    drop_columns = ["validators", "file", "matches_max_priority"]
    for r in all_results:
        for col in drop_columns:
            r.pop(col, None)

    df = pd.DataFrame(all_results)
    df.to_csv("block_analysis.csv", index=False, encoding="utf-8-sig")
    print("\n📁 CSVファイル 'block_analysis.csv' に保存しました（不要なカラム除外済み）。")
