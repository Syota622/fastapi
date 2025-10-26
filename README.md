# Todo App

FastAPI + DynamoDB + Next.jsで構築されたフルスタックTODOアプリケーション

## 技術スタック

### バックエンド
- **FastAPI** - Python Webフレームワーク
- **DynamoDB Local** - ローカル開発用NoSQLデータベース
- **boto3** - AWS SDK for Python
- **Docker** - コンテナ化

### フロントエンド
- **Next.js 15** - React フレームワーク
- **TypeScript** - 型安全性
- **Tailwind CSS** - スタイリング
- **Docker** - コンテナ化

## 機能

- ✅ TODO作成
- ✅ TODO一覧表示
- ✅ TODO完了/未完了の切り替え
- ✅ TODO削除
- ✅ レスポンシブデザイン

## プロジェクト構成

```
fastapi/
├── backend/
│   ├── Dockerfile
│   ├── main.py           # FastAPIアプリケーション
│   ├── database.py       # DynamoDB接続設定
│   ├── models.py         # Pydanticモデル
│   └── requirements.txt  # Python依存関係
├── frontend/
│   ├── Dockerfile
│   ├── app/
│   │   ├── page.tsx      # メインページ
│   │   ├── layout.tsx    # レイアウト
│   │   └── globals.css   # グローバルスタイル
│   ├── package.json
│   ├── tsconfig.json
│   └── tailwind.config.ts
├── docker-compose.yml     # Docker Compose設定
├── dynamodb-data/         # DynamoDBデータ永続化
└── README.md
```

## セットアップと起動

### 前提条件

- Docker
- Docker Compose

### アプリケーションの起動

```bash
# すべてのサービスを起動
docker compose up --build

# バックグラウンドで起動
docker compose up -d --build

# ログを確認
docker compose logs -f

# 特定のサービスのログを確認
docker compose logs -f backend
docker compose logs -f frontend
```

### アクセスURL

起動後、以下のURLでアクセスできます：

- **フロントエンド**: http://localhost:3000
- **バックエンドAPI**: http://localhost:8000
- **APIドキュメント (Swagger UI)**: http://localhost:8000/docs
- **DynamoDB Local**: http://localhost:8001

### サービスの停止

```bash
# すべてのサービスを停止
docker compose down

# ボリュームも含めて削除
docker compose down -v
```

## API エンドポイント

### 1. TODO一覧取得
```bash
GET /todos
```

**レスポンス例:**
```json
[
  {
    "id": "uuid",
    "title": "買い物に行く",
    "description": "牛乳とパンを買う",
    "completed": false,
    "created_at": "2025-10-26T10:00:00",
    "updated_at": "2025-10-26T10:00:00"
  }
]
```

### 2. TODO作成
```bash
POST /todos
Content-Type: application/json

{
  "title": "新しいTODO",
  "description": "説明（任意）"
}
```

### 3. TODO更新
```bash
PUT /todos/{todo_id}
Content-Type: application/json

{
  "title": "更新されたタイトル",
  "description": "更新された説明",
  "completed": true
}
```

### 4. TODO削除
```bash
DELETE /todos/{todo_id}
```

## DynamoDB データの確認方法

### 方法1: AWS CLI（推奨）

AWS CLIをインストールしている場合：

```bash
# テーブル一覧を確認
aws dynamodb list-tables \
  --endpoint-url http://localhost:8001 \
  --region ap-northeast-1

# Todosテーブルの全データを取得
aws dynamodb scan \
  --table-name Todos \
  --endpoint-url http://localhost:8001 \
  --region ap-northeast-1

# 見やすくフォーマットして表示（jqが必要）
aws dynamodb scan \
  --table-name Todos \
  --endpoint-url http://localhost:8001 \
  --region ap-northeast-1 \
  --output json | jq

# テーブルの詳細情報を確認
aws dynamodb describe-table \
  --table-name Todos \
  --endpoint-url http://localhost:8001 \
  --region ap-northeast-1

# 特定のIDでアイテムを取得
aws dynamodb get-item \
  --table-name Todos \
  --key '{"id":{"S":"YOUR_TODO_ID"}}' \
  --endpoint-url http://localhost:8001 \
  --region ap-northeast-1
```

**AWS CLIのインストール:**
```bash
# macOS
brew install awscli

# pip経由
pip install awscli

# インストール確認
aws --version
```

### 方法2: FastAPI経由（最も簡単）

```bash
# TODO一覧を取得
curl http://localhost:8000/todos | jq

# ブラウザでアクセス
# http://localhost:8000/todos
# http://localhost:8000/docs (Swagger UI)
```

### 方法3: Pythonスクリプト

バックエンドコンテナ内で確認：

```bash
# コンテナに入る
docker exec -it fastapi-backend python

# Pythonインタラクティブシェルで実行
>>> import boto3
>>> dynamodb = boto3.resource(
...     'dynamodb',
...     endpoint_url='http://dynamodb:8001',
...     region_name='ap-northeast-1',
...     aws_access_key_id='dummy',
...     aws_secret_access_key='dummy'
... )
>>> table = dynamodb.Table('Todos')
>>> response = table.scan()
>>> for item in response['Items']:
...     print(item)
```

### 方法4: DynamoDB Admin（GUI）

`docker-compose.yml`に以下を追加：

```yaml
  dynamodb-admin:
    image: aaronshaf/dynamodb-admin:latest
    container_name: dynamodb-admin
    ports:
      - "8002:8001"
    environment:
      - DYNAMO_ENDPOINT=http://dynamodb:8001
      - AWS_REGION=ap-northeast-1
      - AWS_ACCESS_KEY_ID=dummy
      - AWS_SECRET_ACCESS_KEY=dummy
    depends_on:
      - dynamodb
```

追加後、再起動して http://localhost:8002 にアクセス

```bash
docker compose up -d
```

### 方法5: curl で直接DynamoDB APIを呼び出す

```bash
# テーブル一覧
curl -X POST http://localhost:8001/ \
  -H "Content-Type: application/x-amz-json-1.0" \
  -H "X-Amz-Target: DynamoDB_20120810.ListTables" \
  -d '{}'

# 全データをスキャン
curl -X POST http://localhost:8001/ \
  -H "Content-Type: application/x-amz-json-1.0" \
  -H "X-Amz-Target: DynamoDB_20120810.Scan" \
  -d '{"TableName":"Todos"}' | jq
```

## 開発

### バックエンドのみ起動

```bash
docker compose up backend dynamodb
```

### フロントエンドのみ起動

```bash
docker compose up frontend
```

### ログの確認

```bash
# すべてのログ
docker compose logs -f

# バックエンドのログ
docker compose logs -f backend

# フロントエンドのログ
docker compose logs -f frontend

# DynamoDBのログ
docker compose logs -f dynamodb
```

### コンテナに入る

```bash
# バックエンドコンテナ
docker exec -it fastapi-backend bash

# フロントエンドコンテナ
docker exec -it nextjs-frontend sh

# DynamoDBコンテナ
docker exec -it dynamodb-local bash
```

## トラブルシューティング

### ポートが既に使用されている

```bash
# 使用中のポートを確認
lsof -i :3000  # フロントエンド
lsof -i :8000  # バックエンド
lsof -i :8001  # DynamoDB

# プロセスを停止
kill -9 <PID>
```

### DynamoDBのデータをリセット

```bash
# コンテナとボリュームを削除
docker compose down -v

# dynamodb-dataディレクトリを削除
rm -rf dynamodb-data

# 再起動
docker compose up --build
```

### コンテナの再ビルド

```bash
# キャッシュを使わずに再ビルド
docker compose build --no-cache

# 再起動
docker compose up
```

## ライセンス

MIT

## 作成者

FastAPI + DynamoDB + Next.js Todo App
