'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import type { User } from '@/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog'
import { Users, Shield, ShieldCheck, UserX, UserCheck } from 'lucide-react'
import { toast } from 'sonner'

export default function AdminUsersPage() {
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const queryClient = useQueryClient()

  const {
    data: users,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['adminUsers'],
    queryFn: async () => {
      const data = await apiClient.getAllUsers()
      return data as User[]
    },
  })

  const updateUserMutation = useMutation({
    mutationFn: async ({ userId, data }: { userId: string; data: { is_active?: boolean; is_super_admin?: boolean } }) => {
      return await apiClient.updateUserAdminFields(userId, data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['adminUsers'] })
      toast.success('User updated successfully')
    },
    onError: (error) => {
      toast.error('Failed to update user')
      console.error('Update user error:', error)
    },
  })

  const handleToggleActive = async (user: User) => {
    await updateUserMutation.mutateAsync({
      userId: user.id,
      data: { is_active: !user.is_active },
    })
  }

  const handleToggleSuperAdmin = async (user: User) => {
    await updateUserMutation.mutateAsync({
      userId: user.id,
      data: { is_super_admin: !user.is_super_admin },
    })
  }

  if (isLoading) {
    return (
      <div className="space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">User Management</h1>
            <p className="text-gray-600 mt-2">Manage all users across the platform</p>
          </div>
        </div>
        <Card>
          <CardContent className="pt-6">
            <div className="animate-pulse space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="flex items-center space-x-4">
                  <div className="h-10 w-10 bg-gray-200 rounded-full"></div>
                  <div className="space-y-2 flex-1">
                    <div className="h-4 bg-gray-200 rounded w-48"></div>
                    <div className="h-3 bg-gray-200 rounded w-32"></div>
                  </div>
                  <div className="h-6 bg-gray-200 rounded w-16"></div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">User Management</h1>
            <p className="text-gray-600 mt-2">Manage all users across the platform</p>
          </div>
        </div>
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <p className="text-red-600">Failed to load users. Please try again.</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">User Management</h1>
          <p className="text-gray-600 mt-2">Manage all users across the platform</p>
        </div>
        <Badge variant="secondary" className="bg-blue-100 text-blue-800 border-blue-200">
          <Users className="w-4 h-4 mr-1" />
          {users?.length || 0} Users
        </Badge>
      </div>

      {/* Users Table */}
      <Card>
        <CardHeader>
          <CardTitle>All Users</CardTitle>
          <CardDescription>
            View and manage user accounts, permissions, and status
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>User</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Joined</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users?.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>
                    <div className="flex items-center space-x-3">
                      <div className="h-8 w-8 rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 flex items-center justify-center text-white text-sm font-semibold">
                        {`${user.first_name?.[0]}${user.last_name?.[0]}`.toUpperCase()}
                      </div>
                      <div>
                        <div className="font-medium">{user.first_name} {user.last_name}</div>
                        <div className="text-sm text-gray-500">{user.title || 'No title'}</div>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>
                    <Badge variant={user.is_active ? "secondary" : "destructive"}>
                      {user.is_active ? (
                        <>
                          <UserCheck className="w-3 h-3 mr-1" />
                          Active
                        </>
                      ) : (
                        <>
                          <UserX className="w-3 h-3 mr-1" />
                          Inactive
                        </>
                      )}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {user.is_super_admin ? (
                      <Badge variant="secondary" className="bg-red-100 text-red-800 border-red-200">
                        <ShieldCheck className="w-3 h-3 mr-1" />
                        Super Admin
                      </Badge>
                    ) : (
                      <Badge variant="outline">User</Badge>
                    )}
                  </TableCell>
                  <TableCell>
                    {new Date(user.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleToggleActive(user)}
                        className={user.is_active ? "text-red-600 hover:text-red-700" : "text-green-600 hover:text-green-700"}
                      >
                        {user.is_active ? (
                          <>
                            <UserX className="w-4 h-4 mr-1" />
                            Deactivate
                          </>
                        ) : (
                          <>
                            <UserCheck className="w-4 h-4 mr-1" />
                            Activate
                          </>
                        )}
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleToggleSuperAdmin(user)}
                        className={user.is_super_admin ? "text-orange-600 hover:text-orange-700" : "text-purple-600 hover:text-purple-700"}
                      >
                        {user.is_super_admin ? (
                          <>
                            <Shield className="w-4 h-4 mr-1" />
                            Remove Admin
                          </>
                        ) : (
                          <>
                            <ShieldCheck className="w-4 h-4 mr-1" />
                            Make Admin
                          </>
                        )}
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}