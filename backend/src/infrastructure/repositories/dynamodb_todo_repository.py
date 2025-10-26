"""
Infrastructure層: DynamoDB TODO リポジトリ実装
"""
from typing import List, Optional
from datetime import datetime
from botocore.exceptions import ClientError

from domain.entities.todo import Todo
from domain.repositories.todo_repository import TodoRepository
from infrastructure.database.dynamodb_client import DynamoDBClient


class DynamoDBTodoRepository(TodoRepository):
    """DynamoDBを使用したTODOリポジトリの実装"""

    def __init__(self, dynamodb_client: DynamoDBClient):
        self.dynamodb_client = dynamodb_client
        self.table_name = "Todos"

    def _get_table(self):
        """テーブルを取得"""
        return self.dynamodb_client.get_table(self.table_name)

    def _item_to_entity(self, item: dict) -> Todo:
        """DynamoDBアイテムをTodoエンティティに変換"""
        return Todo(
            id=item['id'],
            title=item['title'],
            description=item.get('description'),
            completed=item.get('completed', False),
            created_at=datetime.fromisoformat(item['created_at']),
            updated_at=datetime.fromisoformat(item['updated_at'])
        )

    def _entity_to_item(self, todo: Todo) -> dict:
        """TodoエンティティをDynamoDBアイテムに変換"""
        return {
            'id': todo.id,
            'title': todo.title,
            'description': todo.description,
            'completed': todo.completed,
            'created_at': todo.created_at.isoformat(),
            'updated_at': todo.updated_at.isoformat()
        }

    async def find_all(self) -> List[Todo]:
        """全てのTODOを取得"""
        try:
            table = self._get_table()
            response = table.scan()
            items = response.get('Items', [])

            todos = [self._item_to_entity(item) for item in items]
            return todos
        except Exception as e:
            raise Exception(f"TODO一覧取得エラー: {str(e)}")

    async def find_by_id(self, todo_id: str) -> Optional[Todo]:
        """IDでTODOを取得"""
        try:
            table = self._get_table()
            response = table.get_item(Key={'id': todo_id})

            if 'Item' not in response:
                return None

            return self._item_to_entity(response['Item'])
        except ClientError:
            return None
        except Exception as e:
            raise Exception(f"TODO取得エラー: {str(e)}")

    async def save(self, todo: Todo) -> Todo:
        """TODOを保存（作成または更新）"""
        try:
            table = self._get_table()
            item = self._entity_to_item(todo)
            table.put_item(Item=item)

            return todo
        except Exception as e:
            raise Exception(f"TODO保存エラー: {str(e)}")

    async def delete(self, todo_id: str) -> bool:
        """TODOを削除"""
        try:
            table = self._get_table()
            table.delete_item(Key={'id': todo_id})
            return True
        except Exception as e:
            raise Exception(f"TODO削除エラー: {str(e)}")

    async def exists(self, todo_id: str) -> bool:
        """TODOが存在するか確認"""
        try:
            table = self._get_table()
            response = table.get_item(Key={'id': todo_id})
            return 'Item' in response
        except ClientError:
            return False
        except Exception as e:
            raise Exception(f"TODO存在確認エラー: {str(e)}")
