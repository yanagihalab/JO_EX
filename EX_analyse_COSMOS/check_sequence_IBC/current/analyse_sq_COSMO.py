import pandas as pd
import matplotlib.pyplot as plt

# === File paths ===
file_a = "merged_COSMO_ibc_sq_pk.csv"   # CSV_A (send/ack)
file_b = "merged_OSMO_ibc_sq_rv.csv"     # CSV_B (recv)

# === Load CSVs ===
df_a = pd.read_csv(file_a)
df_b = pd.read_csv(file_b)
df_a.columns = df_a.columns.str.strip()
df_b.columns = df_b.columns.str.strip()

# Select necessary columns
df_a = df_a[['channel_id', 'sequence', 'send_time', 'ack_time']]
df_b = df_b[['channel_id', 'sequence', 'recv_time']]

# Parse timestamps
df_a['send_time'] = pd.to_datetime(df_a['send_time'], errors='coerce')
df_a['ack_time'] = pd.to_datetime(df_a['ack_time'], errors='coerce')
df_b['recv_time'] = pd.to_datetime(df_b['recv_time'], errors='coerce')

# === 重複カウント（channel_id + sequence） ===
dupes_a = df_a.duplicated(subset=['channel_id', 'sequence'], keep=False)
dupes_b = df_b.duplicated(subset=['channel_id', 'sequence'], keep=False)

print("\n=== Duplicate Check ===")
print(f"CSV_A: Total rows = {len(df_a)}, Duplicates = {dupes_a.sum()}")
print(f"CSV_B: Total rows = {len(df_b)}, Duplicates = {dupes_b.sum()}")


# === Merge on channel_id + sequence ===
df_merged = pd.merge(
    df_a,
    df_b,
    how='left',
    on=['channel_id', 'sequence']
)

# === Latency calculation ===
df_merged['send_to_recv'] = (df_merged['recv_time'] - df_merged['send_time']).dt.total_seconds()
df_merged['recv_to_ack'] = (df_merged['ack_time'] - df_merged['recv_time']).dt.total_seconds()
df_merged['total_delay'] = (df_merged['ack_time'] - df_merged['send_time']).dt.total_seconds()

# === Show top 5 channels by IBC count ===
print("\n=== Top 5 Channels by Unique IBC Packet Count ===")
channel_counts = df_merged.groupby('channel_id')['sequence'].nunique().sort_values(ascending=False)
print(channel_counts.head(5))

# === Get user input (channel number or full id) ===
user_input = input("\nEnter channel number to analyze (e.g., 141), or leave blank for all: ").strip()
if user_input == "":
    target_channel = None
elif user_input.startswith("channel-"):
    target_channel = user_input
else:
    target_channel = f"channel-{user_input}"

# === Apply filter ===
if target_channel:
    df_filtered = df_merged[df_merged['channel_id'] == target_channel]
    print(f"\n=== Analyzing: {target_channel} ({len(df_filtered)} records) ===")
else:
    df_filtered = df_merged
    print(f"\n=== Analyzing all channels ({len(df_filtered)} records) ===")

# === Show delay samples ===
print("\n=== First 5 records with timestamps and delays ===")
print(df_filtered[['channel_id', 'sequence', 'send_time', 'recv_time', 'ack_time',
                   'send_to_recv', 'recv_to_ack', 'total_delay']].head())

# === Print averages ===
print(f"\n[{target_channel or 'All Channels'}] Average Latency (seconds):")
print(f"Send → Recv : {df_filtered['send_to_recv'].mean():.2f} sec")
print(f"Recv → Ack  : {df_filtered['recv_to_ack'].mean():.2f} sec")
print(f"Total       : {df_filtered['total_delay'].mean():.2f} sec")

# === Count unique IBC packets ===
ibc_count = df_filtered[['channel_id', 'sequence']].drop_duplicates().shape[0]
print(f"\n=== Unique IBC Packets (channel_id + sequence): {ibc_count} ===")

# === Plot latency distribution ===
plt.figure(figsize=(10, 6))
plt.hist(df_filtered['send_to_recv'].dropna(), bins=40, alpha=0.6, label='Send → Recv', density=True)
plt.hist(df_filtered['recv_to_ack'].dropna(), bins=40, alpha=0.6, label='Recv → Ack', density=True)
plt.hist(df_filtered['total_delay'].dropna(), bins=40, alpha=0.5, label='Total', density=True)
plt.title("Latency Distribution of IBC Packets by Stage")
plt.xlabel("Latency (seconds)")
plt.ylabel("Frequency (normalized)")
plt.legend()
plt.grid(True)

# Save figure
output_path = "ibc_delay_distribution_COSMO.png"
plt.savefig(output_path)
plt.close()
print(f"\n📊 Histogram saved to: {output_path}")
