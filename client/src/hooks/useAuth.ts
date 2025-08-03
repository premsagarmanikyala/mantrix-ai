import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiRequest } from '@/lib/queryClient'

interface User {
  id: string
  email: string
  firstName?: string
  lastName?: string
}

interface LoginCredentials {
  email: string
  password: string
}

export function useAuth() {
  const queryClient = useQueryClient()

  const { data: user, isLoading } = useQuery({
    queryKey: ['/api/auth/me'],
    retry: false,
  })

  const loginMutation = useMutation({
    mutationFn: async (credentials: LoginCredentials) => {
      const response = await apiRequest('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify(credentials),
      })
      
      if (response.token) {
        localStorage.setItem('authToken', response.token)
      }
      
      return response
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/auth/me'] })
    },
  })

  const logout = () => {
    localStorage.removeItem('authToken')
    queryClient.clear()
    window.location.reload()
  }

  const login = (credentials: LoginCredentials) => {
    return loginMutation.mutateAsync(credentials)
  }

  return {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    logout,
    isLoggingIn: loginMutation.isPending,
  }
}