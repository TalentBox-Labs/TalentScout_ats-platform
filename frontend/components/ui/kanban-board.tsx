import * as React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "./card"
import { Badge } from "./badge"
import { Avatar, AvatarFallback } from "./avatar"
import { Button } from "./button"
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd'

interface KanbanColumn {
  id: string
  title: string
  color: string
  items: KanbanItem[]
}

interface KanbanItem {
  id: string
  title: string
  subtitle?: string
  avatar?: string
  tags?: string[]
  priority?: 'low' | 'medium' | 'high'
  dueDate?: string
}

interface KanbanBoardProps {
  columns: KanbanColumn[]
  onDragEnd: (result: any) => void
  onItemClick?: (item: KanbanItem) => void
  className?: string
}

export function KanbanBoard({
  columns,
  onDragEnd,
  onItemClick,
  className = ""
}: KanbanBoardProps) {
  const getPriorityColor = (priority?: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'low': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className={`flex gap-6 overflow-x-auto pb-4 ${className}`}>
      <DragDropContext onDragEnd={onDragEnd}>
        {columns.map((column) => (
          <div key={column.id} className="flex-shrink-0 w-80">
            <div className="mb-4">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-gray-900">{column.title}</h3>
                <Badge className={column.color}>
                  {column.items.length}
                </Badge>
              </div>
            </div>

            <Droppable droppableId={column.id}>
              {(provided, snapshot) => (
                <div
                  ref={provided.innerRef}
                  {...provided.droppableProps}
                  className={`space-y-3 min-h-[400px] p-2 rounded-lg transition-colors ${
                    snapshot.isDraggingOver ? 'bg-blue-50' : 'bg-gray-50'
                  }`}
                >
                  {column.items.map((item, index) => (
                    <Draggable
                      key={item.id}
                      draggableId={item.id}
                      index={index}
                    >
                      {(provided, snapshot) => (
                        <Card
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          {...provided.dragHandleProps}
                          className={`cursor-move transition-shadow hover:shadow-md ${
                            snapshot.isDragging ? 'shadow-lg rotate-3' : ''
                          }`}
                          onClick={() => onItemClick?.(item)}
                        >
                          <CardContent className="p-4">
                            <div className="flex items-start space-x-3">
                              {item.avatar && (
                                <Avatar className="h-8 w-8">
                                  <AvatarFallback>
                                    {item.avatar[0]?.toUpperCase()}
                                  </AvatarFallback>
                                </Avatar>
                              )}
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-gray-900 truncate">
                                  {item.title}
                                </p>
                                {item.subtitle && (
                                  <p className="text-xs text-gray-500 truncate">
                                    {item.subtitle}
                                  </p>
                                )}
                                {item.tags && (
                                  <div className="flex flex-wrap gap-1 mt-2">
                                    {item.tags.slice(0, 2).map((tag, idx) => (
                                      <Badge key={idx} variant="secondary" className="text-xs">
                                        {tag}
                                      </Badge>
                                    ))}
                                    {item.tags.length > 2 && (
                                      <Badge variant="secondary" className="text-xs">
                                        +{item.tags.length - 2}
                                      </Badge>
                                    )}
                                  </div>
                                )}
                                <div className="flex items-center justify-between mt-2">
                                  {item.priority && (
                                    <Badge className={`text-xs ${getPriorityColor(item.priority)}`}>
                                      {item.priority}
                                    </Badge>
                                  )}
                                  {item.dueDate && (
                                    <span className="text-xs text-gray-500">
                                      {item.dueDate}
                                    </span>
                                  )}
                                </div>
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
      </DragDropContext>
    </div>
  )
}