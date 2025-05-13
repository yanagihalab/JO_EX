import pandas as pd
import matplotlib.pyplot as plt

# CSVファイルの読み込み（ファイル名は適宜変更）
df = pd.read_csv("current/block_data_temp.csv", parse_dates=['time'])

# time列が正しく読み込まれたか確認
if df['time'].isnull().any():
    print("警告: time列にNaNがあります")

# ブロック生成時間の間隔を計算
df['block_interval'] = df['time'].diff().dt.total_seconds()

# NaNを除去するタイミングを修正
df.dropna(subset=['block_interval'], inplace=True)

# 提案者の出現回数を集計
proposer_counts = df['proposer_address'].value_counts()

# ヒストグラム（取引数の分布）
plt.figure(figsize=(6, 4))
plt.hist(df['num_txs'], bins=range(0, df['num_txs'].max() + 2), edgecolor='black', alpha=0.7)
plt.xlabel("Number of Transactions")
plt.ylabel("Frequency")
plt.title("Distribution of Transactions per Block")
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig("transaction_distribution.png")
plt.close()

# ブロック生成時間の頻度分布ヒストグラムを追加
plt.figure(figsize=(6, 4))
plt.hist(df['block_interval'], bins=100, color='blue')
plt.xlabel("Block Generation Time (seconds)")
plt.ylabel("Frequency")
plt.title("Frequency Distribution of Block Generation Time")
plt.grid(axis='y', linestyle='--')
plt.savefig("block_generation_time_distribution.png")
plt.close()

# ブロック生成時間の推移
plt.figure(figsize=(8, 4))
plt.plot(df['height'], df['block_interval'])
plt.xlabel("Block Height")
plt.ylabel("Block Generation Time (seconds)")
plt.title("Block Generation Time Trend")
plt.grid(alpha=0.7)
plt.savefig("block_generation_time_trend.png")  # ブロック生成時間の推移を画像ファイルとして保存 ここいらない
plt.close()

# 遅いブロックの提案者を確認（2秒以上）
slow_blocks = df[df['block_interval'] >= 2.0][['height', 'proposer_address', 'block_interval']]
print("Slow Blocks (>=2 sec):\n", slow_blocks)

# 取引数とブロック生成時間の相関
tx_time_corr = df[['num_txs', 'block_interval']].corr().iloc[0, 1]
print(f"Correlation between num_txs and block_interval: {tx_time_corr:.2f}")

# n-1番目のnext_proposerとn番目のproposer_addressの一致確認
df.sort_values(by='height', inplace=True)  # 明示的にソート

# proposer_addressを一つ前の行のnext_proposer_addressと照合
df['prev_next_proposer'] = df['next_proposer_address'].shift(1)

# 比較対象となるアドレスを毎回プリント
for index, row in df.iterrows():
    proposer = row['proposer_address']
    prev_next_proposer = row['prev_next_proposer']
    print(f"Comparing proposer_address: {proposer} with previous next_proposer_address: {prev_next_proposer}")

# 比較結果の一致フラグを作成
df['is_match'] = df['proposer_address'] == df['prev_next_proposer']

# 'Unknown'やNaNを除外して一致率を再計算
df_filtered = df.dropna(subset=['next_proposer_address', 'proposer_address'])  # NaNを除外
df_filtered = df_filtered[df_filtered['next_proposer_address'] != 'Unknown']  # 'Unknown'を除外
df_filtered['prev_next_proposer'] = df_filtered['next_proposer_address'].shift(1)
df_filtered['is_match'] = df_filtered['proposer_address'] == df_filtered['prev_next_proposer']

# 一致率を再計算
match_rate_filtered = df_filtered['is_match'].mean()

# データ確認用（高度なデバッグ用）
print("Comparison of next_proposer and proposer_address:")
print(df_filtered[['height', 'proposer_address', 'next_proposer_address', 'prev_next_proposer', 'is_match']])
print(f"Match rate between previous next_proposer and current proposer_address: {df['is_match'].mean():.2%}")
print(f"Match rate (excluding 'Unknown' and NaN): {match_rate_filtered:.2%}")
