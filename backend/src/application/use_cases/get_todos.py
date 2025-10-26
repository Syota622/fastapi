"""
Application層: TODO取得ユースケース
"""
from typing import List, Optional

from domain.entities.todo import Todo
from domain.repositories.todo_repository import TodoRepository


class GetTodosUseCase:
    """TODO一覧取得のユースケース"""

    def __init__(self, todo_repository: TodoRepository):
        self.todo_repository = todo_repository

    async def execute(self) -> List[Todo]:
        """
        全てのTODOを取得する

        Returns:
            TODOのリスト
        """
        todos = await self.todo_repository.find_all()
        return todos


class GetTodoByIdUseCase:
    """TODO単体取得のユースケース"""

    def __init__(self, todo_repository: TodoRepository):
        self.todo_repository = todo_repository

    async def execute(self, todo_id: str) -> Optional[Todo]:
        """
        IDでTODOを取得する

        Args:
            todo_id: TODOID

        Returns:
            TODO（存在しない場合はNone）
        """
        todo = await self.todo_repository.find_by_id(todo_id)
        return todo
