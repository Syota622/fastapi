"""
Application層: TODO更新ユースケース
"""
from typing import Optional

from domain.entities.todo import Todo
from domain.repositories.todo_repository import TodoRepository


class UpdateTodoUseCase:
    """TODO更新のユースケース"""

    def __init__(self, todo_repository: TodoRepository):
        self.todo_repository = todo_repository

    async def execute(
        self,
        todo_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        completed: Optional[bool] = None
    ) -> Optional[Todo]:
        """
        TODOを更新する

        Args:
            todo_id: TODOID
            title: 新しいタイトル（任意）
            description: 新しい説明（任意）
            completed: 完了状態（任意）

        Returns:
            更新されたTODO（存在しない場合はNone）

        Raises:
            ValueError: バリデーションエラー
        """
        # 既存のTODOを取得
        todo = await self.todo_repository.find_by_id(todo_id)

        if todo is None:
            return None

        # エンティティのメソッドを使用して更新
        if title is not None:
            todo.update_title(title)

        if description is not None:
            todo.update_description(description)

        if completed is not None:
            if completed:
                todo.mark_as_completed()
            else:
                todo.mark_as_incomplete()

        # 更新をリポジトリに保存
        updated_todo = await self.todo_repository.save(todo)

        return updated_todo
