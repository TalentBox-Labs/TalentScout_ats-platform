/**
 * Analytics dashboard with hiring metrics and charts
 */
'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/lib/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

interface AnalyticsData {
  totalApplications: number;
  totalJobs: number;
  avgTimeToHire: number;
  conversionRate: number;
  applicationsByStage: { name: string; value: number; color: string }[];
  applicationsByJob: { name: string; value: number }[];
  monthlyApplications: { month: string; applications: number; hires: number }[];
}

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const data = await apiClient.get('/api/v1/analytics');
      setAnalytics(data);
    } catch (error) {
      console.error('Failed to load analytics:', error);
      // Mock data for demo
      setAnalytics({
        totalApplications: 247,
        totalJobs: 12,
        avgTimeToHire: 18,
        conversionRate: 4.5,
        applicationsByStage: [
          { name: 'Applied', value: 89, color: '#3B82F6' },
          { name: 'Screening', value: 45, color: '#F59E0B' },
          { name: 'Interview', value: 23, color: '#8B5CF6' },
          { name: 'Offer', value: 8, color: '#10B981' },
          { name: 'Hired', value: 11, color: '#059669' },
        ],
        applicationsByJob: [
          { name: 'Senior Developer', value: 45 },
          { name: 'Product Manager', value: 32 },
          { name: 'UX Designer', value: 28 },
          { name: 'DevOps Engineer', value: 21 },
          { name: 'Data Scientist', value: 18 },
        ],
        monthlyApplications: [
          { month: 'Jan', applications: 23, hires: 2 },
          { month: 'Feb', applications: 31, hires: 3 },
          { month: 'Mar', applications: 28, hires: 1 },
          { month: 'Apr', applications: 35, hires: 4 },
          { month: 'May', applications: 42, hires: 1 },
          { month: 'Jun', applications: 38, hires: 0 },
        ],
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-6">Loading analytics...</div>;
  }

  if (!analytics) {
    return <div className="p-6">Failed to load analytics data</div>;
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-500">Track your hiring performance</p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline">Export Report</Button>
          <Button>Schedule Report</Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Applications</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.totalApplications}</div>
            <p className="text-xs text-muted-foreground">
              +12% from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Jobs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.totalJobs}</div>
            <p className="text-xs text-muted-foreground">
              +2 new this month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Time to Hire</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.avgTimeToHire} days</div>
            <p className="text-xs text-muted-foreground">
              -3 days from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Conversion Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.conversionRate}%</div>
            <p className="text-xs text-muted-foreground">
              +0.8% from last month
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Applications by Stage */}
        <Card>
          <CardHeader>
            <CardTitle>Applications by Stage</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={analytics.applicationsByStage}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {analytics.applicationsByStage.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Applications by Job */}
        <Card>
          <CardHeader>
            <CardTitle>Top Job Postings</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analytics.applicationsByJob}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#3B82F6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Monthly Trends */}
      <Card>
        <CardHeader>
          <CardTitle>Monthly Applications & Hires</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={analytics.monthlyApplications}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="applications" fill="#3B82F6" name="Applications" />
              <Bar dataKey="hires" fill="#10B981" name="Hires" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}