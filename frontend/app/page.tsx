'use client';

import { useEffect, useState } from 'react';
import TodoForm from '@/components/TodoForm';
import TodoItem from '@/components/TodoItem';

interface Todo {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export default function Home() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // TODO一覧を取得
  const fetchTodos = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${apiUrl}/todos`);

      if (!response.ok) {
        throw new Error('TODO一覧の取得に失敗しました');
      }

      const data = await response.json();
      setTodos(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'エラーが発生しました');
      console.error('Error fetching todos:', err);
    } finally {
      setLoading(false);
    }
  };

  // TODOを作成
  const createTodo = async (title: string, description: string) => {
    try {
      const response = await fetch(`${apiUrl}/todos`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title,
          description: description || null,
        }),
      });

      if (!response.ok) {
        throw new Error('TODOの作成に失敗しました');
      }

      // TODO一覧を再取得
      await fetchTodos();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'TODOの作成に失敗しました');
      throw err;
    }
  };

  // TODOを更新（タイトル・説明）
  const updateTodo = async (id: string, title: string, description: string) => {
    try {
      const response = await fetch(`${apiUrl}/todos/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title,
          description: description || null,
        }),
      });

      if (!response.ok) {
        throw new Error('TODOの更新に失敗しました');
      }

      // TODO一覧を再取得
      await fetchTodos();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'TODOの更新に失敗しました');
      console.error('Error updating todo:', err);
    }
  };

  // 完了状態を切り替え
  const toggleComplete = async (todo: Todo) => {
    try {
      const response = await fetch(`${apiUrl}/todos/${todo.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          completed: !todo.completed,
        }),
      });

      if (!response.ok) {
        throw new Error('TODOの更新に失敗しました');
      }

      // TODO一覧を再取得
      await fetchTodos();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'TODOの更新に失敗しました');
      console.error('Error updating todo:', err);
    }
  };

  // TODOを削除
  const deleteTodo = async (todo: Todo) => {
    if (!confirm(`「${todo.title}」を削除しますか？`)) {
      return;
    }

    try {
      const response = await fetch(`${apiUrl}/todos/${todo.id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('TODOの削除に失敗しました');
      }

      // TODO一覧を再取得
      await fetchTodos();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'TODOの削除に失敗しました');
      console.error('Error deleting todo:', err);
    }
  };

  useEffect(() => {
    fetchTodos();
  }, []);

  return (
    <main className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8 text-gray-800">Todo App</h1>

        {/* TODO作成フォーム */}
        <TodoForm onSubmit={createTodo} />

        {/* ローディング表示 */}
        {loading && (
          <div className="text-center py-8">
            <p className="text-gray-600">読み込み中...</p>
          </div>
        )}

        {/* エラー表示 */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            エラー: {error}
          </div>
        )}

        {/* TODOなし */}
        {!loading && !error && todos.length === 0 && (
          <div className="text-center py-8 bg-white rounded-lg shadow">
            <p className="text-gray-600">TODOがありません</p>
          </div>
        )}

        {/* TODO一覧 */}
        {!loading && !error && todos.length > 0 && (
          <div className="space-y-4">
            {todos.map((todo) => (
              <TodoItem
                key={todo.id}
                todo={todo}
                onToggleComplete={toggleComplete}
                onUpdate={updateTodo}
                onDelete={deleteTodo}
              />
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
