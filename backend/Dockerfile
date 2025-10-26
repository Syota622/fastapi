# Python 3.13をベースイメージとして使用
FROM python:3.13-slim

# 作業ディレクトリを設定
WORKDIR /app

# 環境変数を設定（Pythonのバッファリングを無効化）
ENV PYTHONUNBUFFERED=1

# システムパッケージの更新と必要なパッケージのインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# requirements.txtをコピー
COPY requirements.txt .

# Pythonパッケージのインストール
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# ポート8000を公開
EXPOSE 8000

# FastAPIアプリケーションを起動（クリーンアーキテクチャ版）
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
