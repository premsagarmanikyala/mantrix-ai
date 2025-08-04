import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Edit, Trash2 } from 'lucide-react'
// Make sure userApi is exported from '@/lib/api', or adjust the import to match the actual export.
// For example, if it's exported as 'usersApi', update the import:
// Adjust the import to match the actual exports from '@/lib/api'.
// For example, if the types are exported as 'UserType' and 'UserCreateType':
// Make sure userApi has a delete method, or import the correct API
// Import userApi and ensure it has a 'create' method for creating users
import { userApi } from '@/lib/api'
// If userApi does not have a 'create' method, you need to add it in '@/lib/api' or import the correct API that does.
// If your API uses a different method name, such as 'remove', import and use that instead
// import { usersApi } from '@/lib/api'
// If your types are in 'src/lib/types.ts', use the correct relative path:
type User = {
  id: string | number
  email: string
  username: string
  full_name: string
  bio?: string
}

type UserCreate = {
  email: string
  username: string
  full_name: string
  bio?: string
}

// Or, if you don't have a types file, define them here:
//
// type User = {
//   id: string | number
//   email: string
//   username: string
//   full_name: string
//   bio?: string
// }
//
// type UserCreate = {
//   email: string
//   username: string
//   full_name: string
//   bio?: string
// }
// Or, if userApi is a default export:
// import userApi, { type User, type UserCreate } from '@/lib/api'
// import userApi, { type User, type UserCreate } from '@/lib/api'

export default function Users() {
  const [showCreateForm, setShowCreateForm] = useState(false)
  const queryClient = useQueryClient()
  // Removed unused editingUser state
  const { data: users = [], isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: () => userApi.me().then((res: { data: User[] }) => res.data),
  })

  // Replace 'userApi.create' with the correct method for creating a user.
  // For example, if your API uses 'userApi.add' or 'userApi.register', use that.
  // Here is a fallback example:
  const createMutation = useMutation({
    mutationFn: (payload: { data: UserCreate }) => userApi.add ? userApi.add(payload.data) : Promise.reject(new Error('Create method not found')),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      setShowCreateForm(false)
    },
  })

  // Use the correct method name for deleting a user from your API
  const deleteMutation = useMutation({
    mutationFn: (id: string | number) => userApi.remove ? userApi.remove(id) : Promise.reject(new Error('Delete method not found')),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
    },
  })

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const userData: UserCreate = {
      email: formData.get('email') as string,
      username: formData.get('username') as string,
      full_name: formData.get('full_name') as string,
      bio: formData.get('bio') as string || undefined,
    }
    createMutation.mutate({ data: userData })
  }

  if (isLoading) {
    return <div className="text-center py-8">Loading users...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Users</h1>
        <button
          onClick={() => setShowCreateForm(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add User
        </button>
      </div>

      {showCreateForm && (
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Create New User</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Email
                </label>
                <input
                  type="email"
                  name="email"
                  id="email"
                  required
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
              </div>
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Username
                </label>
                <input
                  type="text"
                  name="username"
                  id="username"
                  required
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
              </div>
            </div>
            <div>
              <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Full Name
              </label>
              <input
                type="text"
                name="full_name"
                id="full_name"
                required
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>
            <div>
              <label htmlFor="bio" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Bio
              </label>
              <textarea
                name="bio"
                id="bio"
                rows={3}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={createMutation.isPending}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {createMutation.isPending ? 'Creating...' : 'Create User'}
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200 dark:divide-gray-700">
          {users.map((user: User) => (
            <li key={user.id} className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="flex-shrink-0 h-10 w-10">
                    <div className="h-10 w-10 rounded-full bg-gray-300 dark:bg-gray-600 flex items-center justify-center">
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        {user.full_name.charAt(0).toUpperCase()}
                      </span>
                    </div>
                  </div>
                  <div className="ml-4">
                    <div className="text-sm font-medium text-gray-900 dark:text-white">
                      {user.full_name}
                    </div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      @{user.username} • {user.email}
                    </div>
                    {user.bio && (
                      <div className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                        {user.bio}
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    // Edit functionality not implemented
                    className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                  >
                    <Edit className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => deleteMutation.mutate(user.id)}
                    className="text-gray-400 hover:text-red-600"
                    disabled={deleteMutation.isPending}
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}