"""
Application層: TODO作成ユースケース
"""
from datetime import datetime
from typing import Optional
import uuid

from domain.entities.todo import Todo
from domain.repositories.todo_repository import TodoRepository


class CreateTodoUseCase:
    """TODO作成のユースケース"""

    def __init__(self, todo_repository: TodoRepository):
        self.todo_repository = todo_repository

    async def execute(
        self,
        title: str,
        description: Optional[str] = None
    ) -> Todo:
        """
        新しいTODOを作成する

        Args:
            title: TODOのタイトル
            description: TODOの説明（任意）

        Returns:
            作成されたTODO

        Raises:
            ValueError: バリデーションエラー
        """
        # 新しいTODOエンティティを作成
        now = datetime.now()
        todo = Todo(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            completed=False,
            created_at=now,
            updated_at=now
        )

        # リポジトリに保存
        saved_todo = await self.todo_repository.save(todo)

        return saved_todo
