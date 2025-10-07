import { useCallback, useState, useEffect } from 'react'
import { createFileRoute } from '@tanstack/react-router'

const TODOS_KEY = 'demo-todos'

// Client-side todo storage using localStorage
function readTodos() {
  try {
    const stored = localStorage.getItem(TODOS_KEY)
    if (stored) {
      return JSON.parse(stored)
    }
  } catch (e) {
    console.error('Failed to read todos from localStorage:', e)
  }
  
  return [
    { id: 1, name: 'Get groceries' },
    { id: 2, name: 'Buy a new phone' },
  ]
}

function saveTodos(todos: any[]) {
  try {
    localStorage.setItem(TODOS_KEY, JSON.stringify(todos))
  } catch (e) {
    console.error('Failed to save todos to localStorage:', e)
  }
}

export const Route = createFileRoute('/demo/start/server-funcs')({
  component: Home,
})

function Home() {
  const [todos, setTodos] = useState<any[]>([])

  useEffect(() => {
    // Load todos from localStorage on component mount
    const initialTodos = readTodos()
    setTodos(initialTodos)
  }, [])

  const [todo, setTodo] = useState('')

  const addTodoHandler = useCallback((todoText: string) => {
    const newTodo = { id: todos.length + 1, name: todoText }
    const updatedTodos = [...todos, newTodo]
    setTodos(updatedTodos)
    saveTodos(updatedTodos)
  }, [todos])

  const submitTodo = useCallback(() => {
    if (todo.trim()) {
      addTodoHandler(todo.trim())
      setTodo('')
    }
  }, [todo, addTodoHandler])

  return (
    <div
      className="flex items-center justify-center min-h-screen bg-gradient-to-br from-zinc-800 to-black p-4 text-white"
      style={{
        backgroundImage:
          'radial-gradient(50% 50% at 20% 60%, #23272a 0%, #18181b 50%, #000000 100%)',
      }}
    >
      <div className="w-full max-w-2xl p-8 rounded-xl backdrop-blur-md bg-black/50 shadow-xl border-8 border-black/10">
        <h1 className="text-2xl mb-4">Client-Side Todo Example</h1>
        <ul className="mb-4 space-y-2">
          {todos?.map((t: any) => (
            <li
              key={t.id}
              className="bg-white/10 border border-white/20 rounded-lg p-3 backdrop-blur-sm shadow-md"
            >
              <span className="text-lg text-white">{t.name}</span>
            </li>
          ))}
        </ul>
        <div className="flex flex-col gap-2">
          <input
            type="text"
            value={todo}
            onChange={(e) => setTodo(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                submitTodo()
              }
            }}
            placeholder="Enter a new todo..."
            className="w-full px-4 py-3 rounded-lg border border-white/20 bg-white/10 backdrop-blur-sm text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent"
          />
          <button
            disabled={todo.trim().length === 0}
            onClick={submitTodo}
            className="bg-blue-500 hover:bg-blue-600 disabled:bg-blue-500/50 disabled:cursor-not-allowed text-white font-bold py-3 px-4 rounded-lg transition-colors"
          >
            Add todo
          </button>
        </div>
      </div>
    </div>
  )
}
