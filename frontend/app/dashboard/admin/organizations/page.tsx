'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import type { Organization } from '@/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Building, Globe, Users, Calendar, ExternalLink } from 'lucide-react'

export default function AdminOrganizationsPage() {
  const {
    data: organizations,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['adminOrganizations'],
    queryFn: async () => {
      const data = await apiClient.getAllOrganizations()
      return data as Organization[]
    },
  })

  if (isLoading) {
    return (
      <div className="space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Organization Management</h1>
            <p className="text-gray-600 mt-2">Manage all organizations on the platform</p>
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
            <h1 className="text-3xl font-bold text-gray-900">Organization Management</h1>
            <p className="text-gray-600 mt-2">Manage all organizations on the platform</p>
          </div>
        </div>
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <p className="text-red-600">Failed to load organizations. Please try again.</p>
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
          <h1 className="text-3xl font-bold text-gray-900">Organization Management</h1>
          <p className="text-gray-600 mt-2">Manage all organizations on the platform</p>
        </div>
        <Badge variant="secondary" className="bg-green-100 text-green-800 border-green-200">
          <Building className="w-4 h-4 mr-1" />
          {organizations?.length || 0} Organizations
        </Badge>
      </div>

      {/* Organizations Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {organizations?.map((org) => (
          <Card key={org.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-center space-x-3">
                <div className="h-10 w-10 rounded-lg bg-gradient-to-r from-green-500 to-blue-600 flex items-center justify-center">
                  <Building className="h-5 w-5 text-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <CardTitle className="text-lg truncate">{org.name}</CardTitle>
                  <CardDescription className="flex items-center">
                    <Calendar className="w-3 h-3 mr-1" />
                    Joined {new Date(org.created_at).toLocaleDateString()}
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {org.website && (
                  <div className="flex items-center text-sm text-gray-600">
                    <Globe className="w-4 h-4 mr-2" />
                    <a
                      href={org.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="hover:text-blue-600 flex items-center"
                    >
                      {org.website}
                      <ExternalLink className="w-3 h-3 ml-1" />
                    </a>
                  </div>
                )}

                {org.industry && (
                  <div className="flex items-center text-sm text-gray-600">
                    <span className="font-medium mr-2">Industry:</span>
                    <Badge variant="outline" className="text-xs">
                      {org.industry}
                    </Badge>
                  </div>
                )}

                {org.size && (
                  <div className="flex items-center text-sm text-gray-600">
                    <Users className="w-4 h-4 mr-2" />
                    <span>{org.size} employees</span>
                  </div>
                )}

                <div className="flex items-center justify-between pt-2">
                  <Badge variant={org.is_active ? "secondary" : "destructive"}>
                    {org.is_active ? 'Active' : 'Inactive'}
                  </Badge>
                  <span className="text-xs text-gray-500">
                    ID: {org.id.slice(0, 8)}...
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {organizations?.length === 0 && (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-8">
              <Building className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No organizations</h3>
              <p className="mt-1 text-sm text-gray-500">
                No organizations have been registered on the platform yet.
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}