'use client'

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import type { User } from '@/types'

interface UserContextType {
  user: User | null
  isLoading: boolean
  error: Error | null
  refetch: () => void
}

const UserContext = createContext<UserContextType | undefined>(undefined)

export function UserProvider({ children }: { children: ReactNode }) {
  const [isClient, setIsClient] = useState(false)

  useEffect(() => {
    setIsClient(true)
  }, [])

  const {
    data: user,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['currentUser'],
    queryFn: async () => {
      const data = await apiClient.getCurrentUser()
      return data as User
    },
    enabled: isClient && !!localStorage.getItem('access_token'),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  return (
    <UserContext.Provider value={{ user: user || null, isLoading, error: error as Error | null, refetch }}>
      {children}
    </UserContext.Provider>
  )
}

export function useUser() {
  const context = useContext(UserContext)
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider')
  }
  return context
}