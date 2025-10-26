"""
FastAPIアプリケーションのエントリーポイント
クリーンアーキテクチャ構成
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from presentation.api.todo_router import router as todo_router
from dependencies import get_dynamodb_client


# FastAPIアプリケーション
app = FastAPI(
    title="Todo API - Clean Architecture",
    version="2.0.0",
    description="クリーンアーキテクチャで構築されたTODOアプリケーション"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に設定してください
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの登録
app.include_router(todo_router)


# 起動時処理
@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時の処理"""
    # DynamoDBテーブルの作成
    dynamodb_client = get_dynamodb_client()
    dynamodb_client.create_todos_table()
    print("アプリケーションが起動しました")


# 終了時処理
@app.on_event("shutdown")
async def shutdown_event():
    """アプリケーション終了時の処理"""
    print("アプリケーションが終了しました")


# ルートエンドポイント
@app.get("/", tags=["health"])
async def root():
    """ヘルスチェック"""
    return {
        "message": "Todo API - Clean Architecture",
        "version": "2.0.0",
        "status": "healthy"
    }


# ヘルスチェック
@app.get("/health", tags=["health"])
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "ok"}
