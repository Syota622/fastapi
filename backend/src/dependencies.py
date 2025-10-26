"""
依存性注入の設定
FastAPIのDependsと組み合わせて使用
"""
from typing import Annotated
from fastapi import Depends

from infrastructure.database.dynamodb_client import DynamoDBClient
from infrastructure.repositories.dynamodb_todo_repository import DynamoDBTodoRepository
from domain.repositories.todo_repository import TodoRepository

from application.use_cases.create_todo import CreateTodoUseCase
from application.use_cases.get_todos import GetTodosUseCase, GetTodoByIdUseCase
from application.use_cases.update_todo import UpdateTodoUseCase
from application.use_cases.delete_todo import DeleteTodoUseCase


# DynamoDBクライアントのシングルトン
_dynamodb_client = None


def get_dynamodb_client() -> DynamoDBClient:
    """DynamoDBクライアントを取得"""
    global _dynamodb_client
    if _dynamodb_client is None:
        _dynamodb_client = DynamoDBClient()
    return _dynamodb_client


def get_todo_repository(
    dynamodb_client: DynamoDBClient = Depends(get_dynamodb_client)
) -> TodoRepository:
    """TODOリポジトリを取得"""
    return DynamoDBTodoRepository(dynamodb_client)


# ユースケースの依存性注入
def get_create_todo_use_case(
    todo_repository: TodoRepository = Depends(get_todo_repository)
) -> CreateTodoUseCase:
    """TODO作成ユースケースを取得"""
    return CreateTodoUseCase(todo_repository)


def get_get_todos_use_case(
    todo_repository: TodoRepository = Depends(get_todo_repository)
) -> GetTodosUseCase:
    """TODO一覧取得ユースケースを取得"""
    return GetTodosUseCase(todo_repository)


def get_get_todo_by_id_use_case(
    todo_repository: TodoRepository = Depends(get_todo_repository)
) -> GetTodoByIdUseCase:
    """TODO単体取得ユースケースを取得"""
    return GetTodoByIdUseCase(todo_repository)


def get_update_todo_use_case(
    todo_repository: TodoRepository = Depends(get_todo_repository)
) -> UpdateTodoUseCase:
    """TODO更新ユースケースを取得"""
    return UpdateTodoUseCase(todo_repository)


def get_delete_todo_use_case(
    todo_repository: TodoRepository = Depends(get_todo_repository)
) -> DeleteTodoUseCase:
    """TODO削除ユースケースを取得"""
    return DeleteTodoUseCase(todo_repository)
