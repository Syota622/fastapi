from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime
import uuid
from botocore.exceptions import ClientError

from database import create_todo_table, get_todo_table
from models import TodoCreate, TodoUpdate, TodoResponse

app = FastAPI(
    title="Todo API",
    version="1.0.0",
    description="FastAPI + DynamoDB で構築されたTODOアプリケーション"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に設定してください
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 起動時にテーブルを作成
@app.on_event("startup")
async def startup_event():
    create_todo_table()

# API 1: TODO一覧取得
@app.get("/todos", response_model=List[TodoResponse])
async def get_todos():
    """全てのTODOを取得"""
    try:
        table = get_todo_table()
        response = table.scan()
        items = response.get('Items', [])

        # DynamoDBのDecimal型を変換
        todos = []
        for item in items:
            todo = {
                'id': item['id'],
                'title': item['title'],
                'description': item.get('description'),
                'completed': item.get('completed', False),
                'created_at': item['created_at'],
                'updated_at': item['updated_at']
            }
            todos.append(todo)

        return todos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# API 2: TODO作成
@app.post("/todos", response_model=TodoResponse, status_code=201)
async def create_todo(todo: TodoCreate):
    """
    新しいTODOを作成

    - **title**: TODOのタイトル（必須）
    - **description**: TODOの説明（任意）
    """
    try:
        table = get_todo_table()

        # 新しいTODOのデータを作成
        todo_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        item = {
            'id': todo_id,
            'title': todo.title,
            'description': todo.description,
            'completed': False,
            'created_at': now,
            'updated_at': now
        }

        # DynamoDBに保存
        table.put_item(Item=item)

        return item
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TODO作成エラー: {str(e)}")

# API 3: TODO更新
@app.put("/todos/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: str, todo: TodoUpdate):
    """
    TODOを更新（部分更新対応）

    - **title**: TODOのタイトル（任意）
    - **description**: TODOの説明（任意）
    - **completed**: 完了状態（任意）
    """
    try:
        table = get_todo_table()

        # 既存のTODOを確認
        try:
            response = table.get_item(Key={'id': todo_id})
            if 'Item' not in response:
                raise HTTPException(status_code=404, detail="TODOが見つかりません")
        except ClientError:
            raise HTTPException(status_code=404, detail="TODOが見つかりません")

        # 更新するフィールドを動的に構築
        update_expression = "SET updated_at = :updated_at"
        expression_values = {':updated_at': datetime.now().isoformat()}

        if todo.title is not None:
            update_expression += ", title = :title"
            expression_values[':title'] = todo.title

        if todo.description is not None:
            update_expression += ", description = :description"
            expression_values[':description'] = todo.description

        if todo.completed is not None:
            update_expression += ", completed = :completed"
            expression_values[':completed'] = todo.completed

        # DynamoDBを更新
        response = table.update_item(
            Key={'id': todo_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ReturnValues="ALL_NEW"
        )

        return response['Attributes']
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TODO更新エラー: {str(e)}")

# API 4: TODO削除
@app.delete("/todos/{todo_id}", status_code=204)
async def delete_todo(todo_id: str):
    """
    TODOを削除

    - **todo_id**: 削除するTODOのID
    """
    try:
        table = get_todo_table()

        # 既存のTODOを確認
        try:
            response = table.get_item(Key={'id': todo_id})
            if 'Item' not in response:
                raise HTTPException(status_code=404, detail="TODOが見つかりません")
        except ClientError:
            raise HTTPException(status_code=404, detail="TODOが見つかりません")

        # TODOを削除
        table.delete_item(Key={'id': todo_id})

        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TODO削除エラー: {str(e)}")
