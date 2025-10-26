"""
Domain層: Todoエンティティ
ビジネスロジックの中核となるドメインオブジェクト
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Todo:
    """
    TODOエンティティ

    ビジネスルールとデータの整合性を保証する
    """
    id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        """バリデーション"""
        if not self.title or not self.title.strip():
            raise ValueError("タイトルは必須です")

        if len(self.title) > 200:
            raise ValueError("タイトルは200文字以内である必要があります")

    def mark_as_completed(self) -> None:
        """TODOを完了状態にする"""
        self.completed = True
        self.updated_at = datetime.now()

    def mark_as_incomplete(self) -> None:
        """TODOを未完了状態にする"""
        self.completed = False
        self.updated_at = datetime.now()

    def update_title(self, new_title: str) -> None:
        """タイトルを更新する"""
        if not new_title or not new_title.strip():
            raise ValueError("タイトルは必須です")

        if len(new_title) > 200:
            raise ValueError("タイトルは200文字以内である必要があります")

        self.title = new_title
        self.updated_at = datetime.now()

    def update_description(self, new_description: Optional[str]) -> None:
        """説明を更新する"""
        self.description = new_description
        self.updated_at = datetime.now()
