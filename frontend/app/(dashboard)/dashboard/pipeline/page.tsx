/**
 * Pipeline/Kanban view for applications
 */
'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { apiClient } from '@/lib/api';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';

interface Application {
  id: string;
  candidate: {
    first_name: string;
    last_name: string;
    email: string;
  };
  job: {
    title: string;
  };
  current_stage: string;
  status: string;
  ai_match_score?: number;
}

export default function PipelinePage() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadApplications();
  }, []);

  const loadApplications = async () => {
    try {
      const data = await apiClient.get('/api/v1/applications');
      setApplications(data);
    } catch (error) {
      console.error('Failed to load applications:', error);
    } finally {
      setLoading(false);
    }
  };

  const stages = [
    { id: 'applied', name: 'Applied', color: 'bg-blue-100 text-blue-800' },
    { id: 'screening', name: 'Screening', color: 'bg-yellow-100 text-yellow-800' },
    { id: 'interview', name: 'Interview', color: 'bg-purple-100 text-purple-800' },
    { id: 'offer', name: 'Offer', color: 'bg-green-100 text-green-800' },
    { id: 'hired', name: 'Hired', color: 'bg-emerald-100 text-emerald-800' },
  ];

  const getApplicationsByStage = (stageId: string) => {
    return applications.filter(app => app.current_stage === stageId);
  };

  const onDragEnd = (result: any) => {
    // TODO: Implement drag and drop functionality
    console.log('Drag ended:', result);
  };

  if (loading) {
    return <div className="p-6">Loading pipeline...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Pipeline</h1>
          <p className="text-gray-500">Track your hiring pipeline</p>
        </div>
        <Button>Export Pipeline</Button>
      </div>

      <DragDropContext onDragEnd={onDragEnd}>
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6">
          {stages.map((stage) => (
            <div key={stage.id} className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-gray-900">{stage.name}</h3>
                <Badge className={stage.color}>
                  {getApplicationsByStage(stage.id).length}
                </Badge>
              </div>

              <Droppable droppableId={stage.id}>
                {(provided) => (
                  <div
                    ref={provided.innerRef}
                    {...provided.droppableProps}
                    className="space-y-3 min-h-[400px]"
                  >
                    {getApplicationsByStage(stage.id).map((application, index) => (
                      <Draggable
                        key={application.id}
                        draggableId={application.id}
                        index={index}
                      >
                        {(provided) => (
                          <Card
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            {...provided.dragHandleProps}
                            className="cursor-move hover:shadow-md transition-shadow"
                          >
                            <CardContent className="p-4">
                              <div className="flex items-start space-x-3">
                                <Avatar className="h-8 w-8">
                                  <AvatarFallback>
                                    {application.candidate.first_name[0]}
                                    {application.candidate.last_name[0]}
                                  </AvatarFallback>
                                </Avatar>
                                <div className="flex-1 min-w-0">
                                  <p className="text-sm font-medium text-gray-900 truncate">
                                    {application.candidate.first_name} {application.candidate.last_name}
                                  </p>
                                  <p className="text-xs text-gray-500 truncate">
                                    {application.job.title}
                                  </p>
                                  {application.ai_match_score && (
                                    <div className="mt-2">
                                      <div className="flex items-center space-x-1">
                                        <span className="text-xs text-gray-500">Match:</span>
                                        <Badge variant="secondary" className="text-xs">
                                          {Math.round(application.ai_match_score)}%
                                        </Badge>
                                      </div>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}
                  </div>
                )}
              </Droppable>
            </div>
          ))}
        </div>
      </DragDropContext>
    </div>
  );
}