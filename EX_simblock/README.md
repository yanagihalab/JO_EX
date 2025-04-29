# SimBlock Docker環境

SimBlockをDockerで簡単に実行できるように構成された環境です。

## 前提条件

- Docker がインストールされていること
- Git がインストールされていること

## インストール方法

1. リポジトリをクローンします。

```bash
git clone https://github.com/yanagihalab/JO_EX.git
```

2. Dockerイメージをビルドします。

```bash
docker build -t simblock-joex .
```

## 使い方

以下のコマンドでSimBlockを実行します。

```bash
docker run --rm -i \
  -v $(pwd)/settings/SimulationConfiguration.java:/app/simblock/simulator/src/main/java/simblock/settings/SimulationConfiguration.java \
  -v $(pwd)/settings/NetworkConfiguration.java:/app/simblock/simulator/src/main/java/simblock/settings/NetworkConfiguration.java \
  -v $(pwd)/output:/app/simblock/simulator/src/dist/output \
  simblock-joex 2>&1 | tee simulation_log.txt
```

実行後、シミュレーション結果は`output`ディレクトリに保存されます。

## ディレクトリ構成

```
.
├── Dockerfile          # Dockerイメージの定義
├── settings            # シミュレーション設定ファイル
│   ├── SimulationConfiguration.java
│   └── NetworkConfiguration.java
└── output              # シミュレーション結果が保存されるディレクトリ
```

## 備考

- 実行時に`output`ディレクトリがない場合は、手動で作成してください。

## ライセンス

SimBlockはApache License 2.0のもとで提供されています。

詳細については[ライセンスファイル](LICENSE)をご確認ください。


https://dsg-titech.github.io/simblock-visualizer/

# SimBlock Docker Environment

## Overview
This repository contains a Dockerized setup for running [SimBlock v0.8.0](https://github.com/dsg-titech/simblock), a blockchain network simulator.

## Requirements
- Docker
- Docker Compose (optional)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yanagihalab/JO_EX.git
```

### 2. Build Docker Image

```bash
docker build -t simblock_JOEX .
```

## Running Simulations

### Directory Preparation

Create the required directories to store simulation outputs:

```bash
mkdir -p simulator/src/dist/output/graph
```

### Run Simulation
Execute the following command to start a simulation:

```bash
docker run --rm -i \
  -v $(pwd)/settings/SimulationConfiguration.java:/app/simblock/simulator/src/main/java/simblock/settings/SimulationConfiguration.java \
  -v $(pwd)/settings/NetworkConfiguration.java:/app/simblock/simulator/src/main/java/simblock/settings/NetworkConfiguration.java \
  -v $(pwd)/output:/app/simblock/simulator/src/dist/output \
  simblock-minimal 2>&1 | tee simulation_log.txt
```

### Verify Outputs
Simulation results are saved in:

```bash
./output/
```

## Troubleshooting

- **"No such file or directory" error:** Ensure the output directories exist as mentioned above.
- **Docker build or runtime errors:** Verify your Dockerfile paths and volume mappings.

## Reference

- Official Repository: [SimBlock GitHub](https://github.com/dsg-titech/simblock)
- Version: v0.8.0

https://dsg-titech.github.io/simblock-visualizer/
