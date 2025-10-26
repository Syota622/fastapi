"""
Application層: TODO削除ユースケース
"""
from domain.repositories.todo_repository import TodoRepository


class DeleteTodoUseCase:
    """TODO削除のユースケース"""

    def __init__(self, todo_repository: TodoRepository):
        self.todo_repository = todo_repository

    async def execute(self, todo_id: str) -> bool:
        """
        TODOを削除する

        Args:
            todo_id: TODOID

        Returns:
            削除成功の場合True、TODOが存在しない場合False
        """
        # TODOの存在確認
        exists = await self.todo_repository.exists(todo_id)

        if not exists:
            return False

        # 削除実行
        result = await self.todo_repository.delete(todo_id)

        return result
