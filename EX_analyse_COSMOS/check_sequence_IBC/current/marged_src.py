import pandas as pd
import glob
import os

# CSVファイルが格納されているフォルダ
folder_path = './COSMO'  # 例: './data'

# 部分一致フィルター対象の文字列
match_keyword = 'COSMO_ibc_sq_rv'

all_csv_files = glob.glob(os.path.join(folder_path, '*.csv'))
target_files = [f for f in all_csv_files if match_keyword in os.path.basename(f)]

df_list = [pd.read_csv(f) for f in target_files]
merged_df = pd.concat(df_list, ignore_index=True)

# 行数を表示
total_rows = len(merged_df)
print(f"結合後の総行数: {total_rows:,} 行")

# 保存
output_path = f'merged_{match_keyword}.csv'
merged_df.to_csv(output_path, index=False)

print(f"{len(target_files)} 件のファイルを結合し、'{output_path}' として保存しました。")
