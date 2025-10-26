"""
Domain層: TODOリポジトリインターフェース
データ永続化の抽象化
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.todo import Todo


class TodoRepository(ABC):
    """
    TODOリポジトリのインターフェース

    具体的な実装はInfrastructure層で行う
    """

    @abstractmethod
    async def find_all(self) -> List[Todo]:
        """全てのTODOを取得"""
        pass

    @abstractmethod
    async def find_by_id(self, todo_id: str) -> Optional[Todo]:
        """IDでTODOを取得"""
        pass

    @abstractmethod
    async def save(self, todo: Todo) -> Todo:
        """TODOを保存（作成または更新）"""
        pass

    @abstractmethod
    async def delete(self, todo_id: str) -> bool:
        """TODOを削除"""
        pass

    @abstractmethod
    async def exists(self, todo_id: str) -> bool:
        """TODOが存在するか確認"""
        pass
