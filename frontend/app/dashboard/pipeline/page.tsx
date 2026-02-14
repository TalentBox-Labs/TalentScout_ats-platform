'use client'

import { useMemo } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import type { Application, JobStage } from '@/types'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

function formatScore(score?: number) {
  if (score == null) return null
  return `${Math.round(score)}%`
}

function getStageKey(app: Application) {
  return app.current_stage_obj?.id || app.current_stage || 'unassigned'
}

function getStageName(app: Application) {
  return app.current_stage_obj?.name || 'Unassigned'
}

export default function PipelinePage() {
  const queryClient = useQueryClient()

  const { data: applications, isLoading, isError } = useQuery({
    queryKey: ['applications'],
    queryFn: async () => (await apiClient.getApplications()) as Application[],
  })

  const moveStageMutation = useMutation({
    mutationFn: async ({
      applicationId,
      stageId,
    }: {
      applicationId: string
      stageId: string
    }) => apiClient.updateApplicationStage(applicationId, stageId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] })
    },
  })

  const screenMutation = useMutation({
    mutationFn: async (applicationId: string) =>
      apiClient.screenCandidate(applicationId),
  })

  const grouped = useMemo(() => {
    const map = new Map<
      string,
      { id: string; name: string; items: Application[] }
    >()

    ;(applications || []).forEach((app) => {
      const key = getStageKey(app)
      const name = getStageName(app)
      if (!map.has(key)) {
        map.set(key, { id: key, name, items: [] })
      }
      map.get(key)!.items.push(app)
    })

    return Array.from(map.values())
  }, [applications])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">AI Hiring Plan</h1>
        <p className="text-sm text-muted-foreground">
          Manage the hiring pipeline and move applications across stages.
        </p>
      </div>

      {isLoading && <p className="text-sm text-muted-foreground">Loading pipeline...</p>}
      {isError && <p className="text-sm text-destructive">Failed to load pipeline.</p>}

      {!isLoading && !isError && grouped.length === 0 && (
        <div className="rounded-lg border bg-card p-6 text-sm text-muted-foreground">
          No applications yet. Create applications to start using the pipeline.
        </div>
      )}

      {!isLoading && !isError && grouped.length > 0 && (
        <div className="grid gap-4 lg:grid-cols-3">
          {grouped.map((stage) => (
            <section key={stage.id} className="rounded-lg border bg-card p-4 shadow-sm">
              <div className="mb-3 flex items-center justify-between">
                <h2 className="text-sm font-medium">{stage.name}</h2>
                <Badge variant="secondary">{stage.items.length}</Badge>
              </div>

              <div className="space-y-3">
                {stage.items.map((app) => {
                  const availableStages: JobStage[] = app.job?.stages || []
                  const currentStageId = app.current_stage || ''
                  const score = formatScore(app.ai_match_score)

                  return (
                    <article key={app.id} className="rounded-md border p-3">
                      <div className="mb-2 flex items-center justify-between gap-2">
                        <p className="truncate text-sm font-medium">
                          {app.candidate?.first_name} {app.candidate?.last_name}
                        </p>
                        <Badge variant="outline" className="capitalize">
                          {app.status}
                        </Badge>
                      </div>

                      <p className="truncate text-xs text-muted-foreground">
                        {app.job?.title || 'Unknown role'}
                      </p>

                      {score && (
                        <p className="mt-2 text-xs text-muted-foreground">
                          AI match score: <span className="font-medium text-foreground">{score}</span>
                        </p>
                      )}

                      <div className="mt-3 flex items-center gap-2">
                        <select
                          className="h-9 flex-1 rounded-md border bg-background px-2 text-sm"
                          value={currentStageId}
                          onChange={(e) =>
                            moveStageMutation.mutate({
                              applicationId: app.id,
                              stageId: e.target.value,
                            })
                          }
                          disabled={availableStages.length === 0 || moveStageMutation.isPending}
                        >
                          {availableStages.length === 0 && (
                            <option value="">No stages</option>
                          )}
                          {availableStages.map((s) => (
                            <option key={s.id} value={s.id}>
                              {s.name}
                            </option>
                          ))}
                        </select>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => screenMutation.mutate(app.id)}
                          disabled={screenMutation.isPending}
                        >
                          Re-screen
                        </Button>
                      </div>
                    </article>
                  )
                })}
              </div>
            </section>
          ))}
        </div>
      )}
    </div>
  )
}
