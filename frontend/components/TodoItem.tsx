'use client';

import { useState } from 'react';

interface Todo {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

interface TodoItemProps {
  todo: Todo;
  onToggleComplete: (todo: Todo) => void;
  onUpdate: (id: string, title: string, description: string) => void;
  onDelete: (todo: Todo) => void;
}

export default function TodoItem({ todo, onToggleComplete, onUpdate, onDelete }: TodoItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(todo.title);
  const [editDescription, setEditDescription] = useState(todo.description || '');

  const handleSave = () => {
    if (!editTitle.trim()) {
      alert('タイトルを入力してください');
      return;
    }
    onUpdate(todo.id, editTitle.trim(), editDescription.trim());
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditTitle(todo.title);
    setEditDescription(todo.description || '');
    setIsEditing(false);
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow">
      {isEditing ? (
        // 編集モード
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              タイトル
            </label>
            <input
              type="text"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-800"
              placeholder="TODOのタイトル"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              説明
            </label>
            <textarea
              value={editDescription}
              onChange={(e) => setEditDescription(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-800"
              placeholder="TODOの説明"
              rows={3}
            />
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleSave}
              className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors"
            >
              保存
            </button>
            <button
              onClick={handleCancel}
              className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg font-medium transition-colors"
            >
              キャンセル
            </button>
          </div>
        </div>
      ) : (
        // 表示モード
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3
              className={`text-xl font-semibold mb-2 ${
                todo.completed ? 'line-through text-gray-500' : 'text-gray-800'
              }`}
            >
              {todo.title}
            </h3>
            {todo.description && (
              <p className="text-gray-600 mb-3">{todo.description}</p>
            )}
            <div className="flex items-center gap-4 text-sm text-gray-500">
              <span
                className={`px-3 py-1 rounded-full ${
                  todo.completed
                    ? 'bg-green-100 text-green-800'
                    : 'bg-yellow-100 text-yellow-800'
                }`}
              >
                {todo.completed ? '完了' : '未完了'}
              </span>
              <span>
                作成: {new Date(todo.created_at).toLocaleDateString('ja-JP')}
              </span>
            </div>
          </div>
          <div className="ml-4 flex flex-col gap-2">
            <button
              onClick={() => setIsEditing(true)}
              className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors"
            >
              編集
            </button>
            <button
              onClick={() => onToggleComplete(todo)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                todo.completed
                  ? 'bg-gray-200 hover:bg-gray-300 text-gray-700'
                  : 'bg-green-500 hover:bg-green-600 text-white'
              }`}
            >
              {todo.completed ? '未完了に戻す' : '完了にする'}
            </button>
            <button
              onClick={() => onDelete(todo)}
              className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-colors"
            >
              削除
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
