from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# リクエスト用モデル
class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

# レスポンス用モデル
class TodoResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    completed: bool
    created_at: str
    updated_at: str
