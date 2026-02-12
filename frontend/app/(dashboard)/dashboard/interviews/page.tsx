/**
 * Interview scheduling and management page
 */
'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Calendar, Clock, MapPin, Video, Users } from 'lucide-react';
import { apiClient } from '@/lib/api';

interface Interview {
  id: string;
  candidate: {
    first_name: string;
    last_name: string;
    email: string;
  };
  job: {
    title: string;
  };
  scheduled_at: string;
  duration: number;
  type: 'phone' | 'video' | 'in-person';
  location?: string;
  interviewers: string[];
  status: 'scheduled' | 'completed' | 'cancelled';
  notes?: string;
}

export default function InterviewsPage() {
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadInterviews();
  }, []);

  const loadInterviews = async () => {
    try {
      const data = await apiClient.getInterviews();
      setInterviews(data);
    } catch (error) {
      console.error('Failed to load interviews:', error);
      // Mock data for demo
      setInterviews([
        {
          id: '1',
          candidate: { first_name: 'John', last_name: 'Doe', email: 'john@example.com' },
          job: { title: 'Senior Developer' },
          scheduled_at: '2024-01-15T14:00:00Z',
          duration: 60,
          type: 'video',
          location: 'Zoom Meeting',
          interviewers: ['Sarah Johnson', 'Mike Chen'],
          status: 'scheduled',
          notes: 'Technical interview focusing on React and Node.js experience',
        },
        {
          id: '2',
          candidate: { first_name: 'Jane', last_name: 'Smith', email: 'jane@example.com' },
          job: { title: 'Product Manager' },
          scheduled_at: '2024-01-16T10:00:00Z',
          duration: 45,
          type: 'phone',
          interviewers: ['David Wilson'],
          status: 'scheduled',
          notes: 'Initial screening call',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'scheduled': return 'bg-blue-100 text-blue-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'video': return <Video className="h-4 w-4" />;
      case 'phone': return <Clock className="h-4 w-4" />;
      case 'in-person': return <MapPin className="h-4 w-4" />;
      default: return <Users className="h-4 w-4" />;
    }
  };

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return {
      date: date.toLocaleDateString(),
      time: date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
  };

  if (loading) {
    return <div className="p-6">Loading interviews...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Interviews</h1>
          <p className="text-gray-500">Schedule and manage candidate interviews</p>
        </div>
        <Button>Schedule Interview</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {interviews.map((interview) => {
          const { date, time } = formatDateTime(interview.scheduled_at);

          return (
            <Card key={interview.id} className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <Avatar className="h-10 w-10">
                      <AvatarFallback>
                        {interview.candidate.first_name[0]}
                        {interview.candidate.last_name[0]}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <CardTitle className="text-lg">
                        {interview.candidate.first_name} {interview.candidate.last_name}
                      </CardTitle>
                      <p className="text-sm text-gray-500">{interview.job.title}</p>
                    </div>
                  </div>
                  <Badge className={getStatusColor(interview.status)}>
                    {interview.status}
                  </Badge>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <Calendar className="h-4 w-4" />
                  <span>{date} at {time}</span>
                </div>

                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <Clock className="h-4 w-4" />
                  <span>{interview.duration} minutes</span>
                </div>

                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  {getTypeIcon(interview.type)}
                  <span className="capitalize">{interview.type}</span>
                  {interview.location && <span>• {interview.location}</span>}
                </div>

                <div className="space-y-2">
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <Users className="h-4 w-4" />
                    <span>Interviewers:</span>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {interview.interviewers.map((interviewer, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {interviewer}
                      </Badge>
                    ))}
                  </div>
                </div>

                {interview.notes && (
                  <div className="pt-2 border-t">
                    <p className="text-sm text-gray-600">{interview.notes}</p>
                  </div>
                )}

                <div className="flex space-x-2 pt-2">
                  <Button variant="outline" size="sm" className="flex-1">
                    Reschedule
                  </Button>
                  <Button variant="outline" size="sm" className="flex-1">
                    Join Call
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {interviews.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Calendar className="h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No interviews scheduled</h3>
            <p className="text-gray-500 text-center mb-4">
              Schedule your first interview to get started with the hiring process.
            </p>
            <Button>Schedule Interview</Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}