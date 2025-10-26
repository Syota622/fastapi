"""
Presentation層: TODO APIルーター
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List

from presentation.schemas.todo_schema import (
    TodoCreateRequest,
    TodoUpdateRequest,
    TodoResponse
)
from application.use_cases.create_todo import CreateTodoUseCase
from application.use_cases.get_todos import GetTodosUseCase, GetTodoByIdUseCase
from application.use_cases.update_todo import UpdateTodoUseCase
from application.use_cases.delete_todo import DeleteTodoUseCase
from domain.entities.todo import Todo
from dependencies import (
    get_create_todo_use_case,
    get_get_todos_use_case,
    get_get_todo_by_id_use_case,
    get_update_todo_use_case,
    get_delete_todo_use_case
)


router = APIRouter(prefix="/todos", tags=["todos"])


def _todo_to_response(todo: Todo) -> TodoResponse:
    """Todoエンティティをレスポンススキーマに変換"""
    return TodoResponse(
        id=todo.id,
        title=todo.title,
        description=todo.description,
        completed=todo.completed,
        created_at=todo.created_at,
        updated_at=todo.updated_at
    )


@router.get("", response_model=List[TodoResponse], summary="TODO一覧取得")
async def get_todos(
    get_todos_use_case: GetTodosUseCase = Depends(get_get_todos_use_case)
):
    """
    全てのTODOを取得

    Returns:
        TODOのリスト
    """
    try:
        todos = await get_todos_use_case.execute()
        return [_todo_to_response(todo) for todo in todos]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"TODO一覧取得エラー: {str(e)}"
        )


@router.get("/{todo_id}", response_model=TodoResponse, summary="TODO取得")
async def get_todo(
    todo_id: str,
    get_todo_by_id_use_case: GetTodoByIdUseCase = Depends(get_get_todo_by_id_use_case)
):
    """
    IDでTODOを取得

    Args:
        todo_id: TODO ID

    Returns:
        TODO

    Raises:
        404: TODOが見つからない
    """
    try:
        todo = await get_todo_by_id_use_case.execute(todo_id)

        if todo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="TODOが見つかりません"
            )

        return _todo_to_response(todo)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"TODO取得エラー: {str(e)}"
        )


@router.post(
    "",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="TODO作成"
)
async def create_todo(
    request: TodoCreateRequest,
    create_todo_use_case: CreateTodoUseCase = Depends(get_create_todo_use_case)
):
    """
    新しいTODOを作成

    Args:
        request: TODO作成リクエスト

    Returns:
        作成されたTODO

    Raises:
        400: バリデーションエラー
    """
    try:
        todo = await create_todo_use_case.execute(
            title=request.title,
            description=request.description
        )
        return _todo_to_response(todo)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"TODO作成エラー: {str(e)}"
        )


@router.put("/{todo_id}", response_model=TodoResponse, summary="TODO更新")
async def update_todo(
    todo_id: str,
    request: TodoUpdateRequest,
    update_todo_use_case: UpdateTodoUseCase = Depends(get_update_todo_use_case)
):
    """
    TODOを更新

    Args:
        todo_id: TODO ID
        request: TODO更新リクエスト

    Returns:
        更新されたTODO

    Raises:
        404: TODOが見つからない
        400: バリデーションエラー
    """
    try:
        todo = await update_todo_use_case.execute(
            todo_id=todo_id,
            title=request.title,
            description=request.description,
            completed=request.completed
        )

        if todo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="TODOが見つかりません"
            )

        return _todo_to_response(todo)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"TODO更新エラー: {str(e)}"
        )


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT, summary="TODO削除")
async def delete_todo(
    todo_id: str,
    delete_todo_use_case: DeleteTodoUseCase = Depends(get_delete_todo_use_case)
):
    """
    TODOを削除

    Args:
        todo_id: TODO ID

    Raises:
        404: TODOが見つからない
    """
    try:
        result = await delete_todo_use_case.execute(todo_id)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="TODOが見つかりません"
            )

        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"TODO削除エラー: {str(e)}"
        )
