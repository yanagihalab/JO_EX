# EX_analyse_COSMOSについての説明（Cosmos Blockchainの分析）

## jupyterを利用しない場合

### Python仮想環境を作成し、仮想環境を作成する（以下はおさらい。）
- Pythonのバージョンが複数インストールされていたとしても、仮想環境を作成する際に使用したPythonのバージョンが仮想環境内では固定的に使われる

- リポジトリ内に移動
```bash
cd EX_analyse_BC
```

- 仮想環境作成
- 最初のvenvは仮想環境を作るためのPythonモジュール名
- 後ろの3.12は仮想環境を入れておくディレクトリ名で、これが仮想環境名になる
- 仮想環境を複数作って使い分ける場合、後ろの3.12を分かりやすい名前に変えると良い
- 仮想環境のディレクトリはどこに作っても良いが、リポジトリを削除した際に一緒に削除されるよう、今回はリポジトリ内に作成する

```bash
py -3.12 -m venv "xxx"
```

- 仮想環境に切り替える
```bash
3.12\scripts\activate
```
- プロンプトの左に(3.12)が付くのを確認

- Pythonのバージョンを確認
```bash
python -V
```

### Pythonライブラリのインストール
```bash
pip install -r requirements.txt
```

- この状態で必要なライブラリがインストール済みの仮想環境ができあがったので、Pythonプログラムを実行できる

### 仮想環境から抜け出す
```bash
deactivate
```
- プロンプトの左の(3.12)が消えたのを確認


## 2. Pythonプログラム
- リポジトリ内に移動(移動済みであればスキップ)
```bash
cd EX_analyse_BC
```

- 仮想環境に切り替える(切り替え済みであればスキップ)
```bash
3.12\scripts\activate
```
- プロンプトの左に(3.12)が付くのを確認

### jupyterを利用する場合
```bash
cd EX_analyse_BC_jupyter
```


(提出先及び共有ファイル)[https://susadmin-my.sharepoint.com/personal/yanagihara_takaaki_rs_sus_ac_jp/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Fyanagihara%5Ftakaaki%5Frs%5Fsus%5Fac%5Fjp%2FDocuments%2FJO%5FEX&ga=1]