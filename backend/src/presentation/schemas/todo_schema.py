"""
Presentation層: TODOスキーマ定義
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TodoCreateRequest(BaseModel):
    """TODO作成リクエスト"""
    title: str = Field(..., min_length=1, max_length=200, description="TODOのタイトル")
    description: Optional[str] = Field(None, description="TODOの説明")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "買い物に行く",
                "description": "牛乳とパンを買う"
            }
        }


class TodoUpdateRequest(BaseModel):
    """TODO更新リクエスト"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="TODOのタイトル")
    description: Optional[str] = Field(None, description="TODOの説明")
    completed: Optional[bool] = Field(None, description="完了状態")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "買い物に行く（更新）",
                "description": "牛乳、パン、卵を買う",
                "completed": True
            }
        }


class TodoResponse(BaseModel):
    """TODOレスポンス"""
    id: str = Field(..., description="TODO ID")
    title: str = Field(..., description="TODOのタイトル")
    description: Optional[str] = Field(None, description="TODOの説明")
    completed: bool = Field(..., description="完了状態")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "買い物に行く",
                "description": "牛乳とパンを買う",
                "completed": False,
                "created_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-01T12:00:00"
            }
        }
