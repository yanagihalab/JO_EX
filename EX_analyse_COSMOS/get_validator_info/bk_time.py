import pandas as pd
import matplotlib.pyplot as plt

# 正しくここで skiprows と header を指定する
df = pd.read_csv("block_analysis.csv", skiprows=1, header=None)

# Convert timestamp strings to datetime
timestamps = pd.to_datetime(df[1], format="%Y-%m-%dT%H:%M:%S.%f%z", errors='coerce')

# Compute time differences in seconds
time_diffs = timestamps.diff().dropna().dt.total_seconds()

# Plot - linear scale
plt.figure(figsize=(10, 6))
plt.hist(time_diffs, bins=1000)
plt.title("Block Time Differences (Linear Scale)")
plt.xlabel("Time Difference (seconds)")
plt.ylabel("Frequency")
plt.grid(True)
plt.tight_layout()
plt.savefig("block_time_diff_linear.png")

# Plot - log scale (Y axis)
plt.figure(figsize=(10, 6))
plt.hist(time_diffs, bins=100, log=True)
plt.title("Block Time Differences (Logarithmic Y Scale)")
plt.xlabel("Time Difference (seconds)")
plt.ylabel("Log-Frequency")
plt.grid(True, which="both", linestyle="--", linewidth=0.5)
plt.tight_layout()
plt.savefig("block_time_diff_log.png")