# クリーンアーキテクチャ実装ガイド

このドキュメントでは、本プロジェクトで実装されているクリーンアーキテクチャの構造と設計思想を詳しく説明します。

## 目次
1. [クリーンアーキテクチャとは](#クリーンアーキテクチャとは)
2. [レイヤー構成](#レイヤー構成)
3. [依存関係のルール](#依存関係のルール)
4. [各レイヤーの詳細](#各レイヤーの詳細)
5. [データフロー](#データフロー)
6. [実装例: TODO作成処理](#実装例-todo作成処理)

---

## クリーンアーキテクチャとは

クリーンアーキテクチャは、Robert C. Martin（Uncle Bob）が提唱したソフトウェア設計手法です。

### 主な目的
- **ビジネスロジックの独立性**: フレームワークやデータベースから独立
- **テスタビリティ**: 各層を独立してテストできる
- **保守性**: 変更が他の層に影響しにくい
- **柔軟性**: 技術スタックの変更が容易

### 基本原則
1. **依存性逆転の原則（DIP）**: 外側の層が内側の層に依存する（逆はNG）
2. **単一責任の原則（SRP）**: 各層が明確な責任を持つ
3. **インターフェース分離の原則（ISP）**: 抽象に依存し、具象に依存しない

---

## レイヤー構成

本プロジェクトは以下の4つの層で構成されています：

```
┌──────────────────────────────────────┐
│     Presentation Layer (外側)        │  ← Web API、スキーマ
│  /src/presentation/                  │
├──────────────────────────────────────┤
│     Application Layer                │  ← ユースケース
│  /src/application/                   │
├──────────────────────────────────────┤
│     Domain Layer (内側/中核)         │  ← エンティティ、リポジトリIF
│  /src/domain/                        │
├──────────────────────────────────────┤
│     Infrastructure Layer (外側)      │  ← DB実装、外部サービス
│  /src/infrastructure/                │
└──────────────────────────────────────┘
```

---

## 依存関係のルール

### 依存の方向
```
Presentation → Application → Domain ← Infrastructure
                                ↑
                            抽象に依存
```

### 重要なポイント
- **Domain層**: 他のどの層にも依存しない（最も内側）
- **Application層**: Domain層のみに依存
- **Presentation層**: Application層とDomain層に依存
- **Infrastructure層**: Domain層の**インターフェース**を実装（具象に依存しない）

---

## 各レイヤーの詳細

### 1. Domain Layer（ドメイン層）
**役割**: ビジネスロジックの中核

**場所**: `/backend/src/domain/`

#### 1.1 エンティティ（Entities）
ビジネスルールとデータの整合性を保証するオブジェクト

**ファイル**: `domain/entities/todo.py`

```python
@dataclass
class Todo:
    """TODOエンティティ - ビジネスルールを持つ"""
    id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        """バリデーション - ビジネスルール"""
        if not self.title or not self.title.strip():
            raise ValueError("タイトルは必須です")
        if len(self.title) > 200:
            raise ValueError("タイトルは200文字以内である必要があります")

    def mark_as_completed(self) -> None:
        """ビジネスロジック: 完了状態に変更"""
        self.completed = True
        self.updated_at = datetime.now()
```

**特徴**:
- データベースやフレームワークに依存しない
- ビジネスルールを内包（バリデーション、状態変更ロジック）
- 純粋なPythonクラス

#### 1.2 リポジトリインターフェース（Repository Interface）
データ永続化の**抽象化**

**ファイル**: `domain/repositories/todo_repository.py`

```python
class TodoRepository(ABC):
    """リポジトリインターフェース - 実装の詳細は隠蔽"""

    @abstractmethod
    async def find_all(self) -> List[Todo]:
        """全てのTODOを取得"""
        pass

    @abstractmethod
    async def save(self, todo: Todo) -> Todo:
        """TODOを保存"""
        pass
```

**重要**:
- このインターフェースはDomain層に配置
- 実装（DynamoDBなど）はInfrastructure層
- これにより**依存性逆転の原則**を実現

---

### 2. Application Layer（アプリケーション層）
**役割**: ユースケース（ビジネスユースケース）の実装

**場所**: `/backend/src/application/use_cases/`

#### ユースケースの例: TODO作成

**ファイル**: `application/use_cases/create_todo.py`

```python
class CreateTodoUseCase:
    """TODO作成のユースケース"""

    def __init__(self, todo_repository: TodoRepository):
        # リポジトリの「インターフェース」に依存
        self.todo_repository = todo_repository

    async def execute(self, title: str, description: Optional[str] = None) -> Todo:
        """
        新しいTODOを作成する

        1. Todoエンティティを作成（バリデーション含む）
        2. リポジトリに保存
        3. 作成されたTodoを返す
        """
        now = datetime.now()
        todo = Todo(
            id=str(uuid.uuid4()),
            title=title,  # ここでTodoのバリデーションが動く
            description=description,
            completed=False,
            created_at=now,
            updated_at=now
        )

        saved_todo = await self.todo_repository.save(todo)
        return saved_todo
```

**特徴**:
- 1つのユースケース = 1つのビジネス操作
- リポジトリの**インターフェース**のみに依存
- 具体的な実装（DynamoDBなど）を知らない
- テストが容易（モックリポジトリを注入できる）

---

### 3. Infrastructure Layer（インフラストラクチャ層）
**役割**: 外部技術の具体的な実装

**場所**: `/backend/src/infrastructure/`

#### 3.1 データベースクライアント

**ファイル**: `infrastructure/database/dynamodb_client.py`

DynamoDBへの接続とテーブル管理

#### 3.2 リポジトリ実装

**ファイル**: `infrastructure/repositories/dynamodb_todo_repository.py`

```python
class DynamoDBTodoRepository(TodoRepository):
    """DynamoDBを使った具体的な実装"""

    def __init__(self, dynamodb_client: DynamoDBClient):
        self.dynamodb_client = dynamodb_client
        self.table_name = "Todos"

    async def save(self, todo: Todo) -> Todo:
        """Todoエンティティ → DynamoDBアイテムに変換して保存"""
        table = self._get_table()
        item = self._entity_to_item(todo)  # 変換処理
        table.put_item(Item=item)
        return todo

    def _entity_to_item(self, todo: Todo) -> dict:
        """エンティティをDBアイテムに変換"""
        return {
            'id': todo.id,
            'title': todo.title,
            'description': todo.description,
            'completed': todo.completed,
            'created_at': todo.created_at.isoformat(),
            'updated_at': todo.updated_at.isoformat()
        }
```

**重要なポイント**:
- Domain層の`TodoRepository`インターフェースを実装
- DB固有の処理（DynamoDB SDK）はこの層に閉じ込める
- エンティティ ⇔ DBアイテムの変換を担当

---

### 4. Presentation Layer（プレゼンテーション層）
**役割**: 外部とのインターフェース（Web API）

**場所**: `/backend/src/presentation/`

#### 4.1 スキーマ（Schemas）

**ファイル**: `presentation/schemas/todo_schema.py`

```python
class TodoCreateRequest(BaseModel):
    """リクエストスキーマ - クライアントから受け取るデータ"""
    title: str
    description: Optional[str] = None

class TodoResponse(BaseModel):
    """レスポンススキーマ - クライアントに返すデータ"""
    id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime
```

#### 4.2 APIルーター

**ファイル**: `presentation/api/todo_router.py`

```python
@router.post("", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    request: TodoCreateRequest,
    create_todo_use_case: CreateTodoUseCase = Depends(get_create_todo_use_case)
):
    """TODO作成エンドポイント"""
    try:
        # ユースケースを実行（依存性注入で取得）
        todo = await create_todo_use_case.execute(
            title=request.title,
            description=request.description
        )
        # エンティティをレスポンススキーマに変換
        return _todo_to_response(todo)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

**特徴**:
- HTTPリクエスト/レスポンスの処理
- ユースケースの呼び出し
- エラーハンドリング
- エンティティ → レスポンススキーマの変換

---

## 依存性注入（Dependency Injection）

**ファイル**: `dependencies.py`

```python
def get_todo_repository(
    dynamodb_client: DynamoDBClient = Depends(get_dynamodb_client)
) -> TodoRepository:
    """リポジトリの具体的な実装を返す"""
    return DynamoDBTodoRepository(dynamodb_client)

def get_create_todo_use_case(
    todo_repository: TodoRepository = Depends(get_todo_repository)
) -> CreateTodoUseCase:
    """ユースケースにリポジトリを注入"""
    return CreateTodoUseCase(todo_repository)
```

### なぜ依存性注入が必要？

1. **テストが容易**: モックリポジトリに差し替え可能
2. **柔軟性**: DynamoDB → PostgreSQLへの切り替えが容易
3. **疎結合**: 各層が具体的な実装に依存しない

---

## データフロー

### TODO作成のフロー例

```
1. クライアント
   ↓ POST /todos { "title": "買い物", "description": "牛乳を買う" }

2. Presentation Layer (todo_router.py)
   ↓ リクエストを受け取る
   ↓ TodoCreateRequestにパース

3. Application Layer (create_todo.py)
   ↓ ユースケースを実行
   ↓ Todoエンティティを作成（バリデーション実行）

4. Domain Layer (todo.py)
   ↓ ビジネスルール検証（タイトルの長さなど）

5. Infrastructure Layer (dynamodb_todo_repository.py)
   ↓ エンティティをDynamoDBアイテムに変換
   ↓ DynamoDBに保存

6. 結果が逆順で返る
   Infrastructure → Application → Presentation

7. Presentation Layer
   ↓ TodoエンティティをTodoResponseに変換
   ↓ JSONレスポンスとして返す

8. クライアント
   ← 201 Created { "id": "...", "title": "買い物", ... }
```

---

## 実装例: TODO作成処理

### 1. クライアントがリクエストを送信
```http
POST /todos
Content-Type: application/json

{
  "title": "買い物",
  "description": "牛乳を買う"
}
```

### 2. Presentation層（ルーター）が受け取る
**ファイル**: `presentation/api/todo_router.py:103-134`

```python
@router.post("", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    request: TodoCreateRequest,  # ← リクエストスキーマにパース
    create_todo_use_case: CreateTodoUseCase = Depends(get_create_todo_use_case)  # ← DI
):
    todo = await create_todo_use_case.execute(
        title=request.title,
        description=request.description
    )
    return _todo_to_response(todo)  # ← エンティティをレスポンスに変換
```

### 3. Application層（ユースケース）が処理
**ファイル**: `application/use_cases/create_todo.py:18-50`

```python
class CreateTodoUseCase:
    def __init__(self, todo_repository: TodoRepository):  # ← インターフェースに依存
        self.todo_repository = todo_repository

    async def execute(self, title: str, description: Optional[str] = None) -> Todo:
        # Todoエンティティを作成（バリデーション発火）
        todo = Todo(
            id=str(uuid.uuid4()),
            title=title,  # ← ここで__post_init__のバリデーションが動く
            description=description,
            completed=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # リポジトリに保存
        saved_todo = await self.todo_repository.save(todo)
        return saved_todo
```

### 4. Domain層（エンティティ）がバリデーション
**ファイル**: `domain/entities/todo.py:24-30`

```python
def __post_init__(self):
    """バリデーション - ビジネスルール"""
    if not self.title or not self.title.strip():
        raise ValueError("タイトルは必須です")

    if len(self.title) > 200:
        raise ValueError("タイトルは200文字以内である必要があります")
```

### 5. Infrastructure層（リポジトリ実装）が保存
**ファイル**: `infrastructure/repositories/dynamodb_todo_repository.py:73-82`

```python
async def save(self, todo: Todo) -> Todo:
    """Todoをデータベースに保存"""
    table = self._get_table()
    item = self._entity_to_item(todo)  # ← エンティティをDBアイテムに変換
    table.put_item(Item=item)
    return todo

def _entity_to_item(self, todo: Todo) -> dict:
    """エンティティ → DynamoDBアイテム"""
    return {
        'id': todo.id,
        'title': todo.title,
        'description': todo.description,
        'completed': todo.completed,
        'created_at': todo.created_at.isoformat(),
        'updated_at': todo.updated_at.isoformat()
    }
```

### 6. レスポンスがクライアントに返る
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "title": "買い物",
  "description": "牛乳を買う",
  "completed": false,
  "created_at": "2025-10-26T10:30:00",
  "updated_at": "2025-10-26T10:30:00"
}
```

---

## クリーンアーキテクチャの利点

### 1. データベースの切り替えが容易

**例**: DynamoDB → PostgreSQLに変更する場合

変更が必要なファイル:
- `infrastructure/repositories/postgres_todo_repository.py`（新規作成）
- `dependencies.py`（注入するリポジトリを変更）

**変更不要**:
- Domain層（エンティティ、リポジトリIF）
- Application層（全ユースケース）
- Presentation層（ルーター、スキーマ）

### 2. テストが容易

```python
# ユースケースのテスト例
def test_create_todo():
    # モックリポジトリを作成
    mock_repository = MockTodoRepository()

    # ユースケースに注入
    use_case = CreateTodoUseCase(mock_repository)

    # テスト実行（DBに接続せずテストできる）
    todo = await use_case.execute(title="テスト")
    assert todo.title == "テスト"
```

### 3. ビジネスロジックが明確

- エンティティ: ビジネスルール（バリデーション、状態変更）
- ユースケース: ビジネス操作（TODO作成、更新など）
- これらがフレームワークから独立

---

## ディレクトリ構造の整理

```
backend/src/
├── domain/                    # Domain層（中核）
│   ├── entities/              # エンティティ
│   │   └── todo.py           # Todoエンティティ
│   └── repositories/          # リポジトリIF
│       └── todo_repository.py # TodoRepositoryインターフェース
│
├── application/               # Application層
│   └── use_cases/             # ユースケース
│       ├── create_todo.py    # TODO作成
│       ├── get_todos.py      # TODO取得
│       ├── update_todo.py    # TODO更新
│       └── delete_todo.py    # TODO削除
│
├── infrastructure/            # Infrastructure層
│   ├── database/              # DB接続
│   │   └── dynamodb_client.py
│   └── repositories/          # リポジトリ実装
│       └── dynamodb_todo_repository.py  # DynamoDB実装
│
├── presentation/              # Presentation層
│   ├── api/                   # APIルーター
│   │   └── todo_router.py
│   └── schemas/               # スキーマ
│       └── todo_schema.py
│
├── dependencies.py            # 依存性注入
└── main.py                    # エントリーポイント
```

---

## まとめ

### クリーンアーキテクチャの3つの核心

1. **依存性逆転**: 外側が内側に依存、内側は外側を知らない
2. **抽象化**: インターフェースに依存し、具象に依存しない
3. **分離**: 各層が明確な責任を持ち、疎結合

### 本実装のキーポイント

- **Domain層**: ビジネスルール（Todo）とリポジトリIF
- **Application層**: ビジネスユースケース（CRUD操作）
- **Infrastructure層**: 具体的な実装（DynamoDB）
- **Presentation層**: Web API（FastAPI）
- **依存性注入**: FastAPIのDependsで各層を接続

この構造により、**テスタビリティ**、**保守性**、**柔軟性**が大幅に向上します。
