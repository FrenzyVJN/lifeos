import { create } from 'zustand'
import type { LifeOSData, GraphNode, GraphEdge } from './types'

interface GraphState {
  data: LifeOSData | null
  loading: boolean
  error: string | null
  selectedNode: GraphNode | null
  hoveredNode: GraphNode | null
  viewMode: 'all' | 'projects' | 'tasks' | 'timeline'
  dateRange: [Date, Date] | null

  setData: (data: LifeOSData) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  selectNode: (node: GraphNode | null) => void
  hoverNode: (node: GraphNode | null) => void
  setViewMode: (mode: 'all' | 'projects' | 'tasks' | 'timeline') => void
  setDateRange: (range: [Date, Date] | null) => void
  fetchData: () => Promise<void>
}

export const useGraphStore = create<GraphState>((set) => ({
  data: null,
  loading: true,
  error: null,
  selectedNode: null,
  hoveredNode: null,
  viewMode: 'all',
  dateRange: null,

  setData: (data) => set({ data }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  selectNode: (node) => set({ selectedNode: node }),
  hoverNode: (node) => set({ hoveredNode: node }),
  setViewMode: (mode) => set({ viewMode: mode }),
  setDateRange: (range) => set({ dateRange: range }),

  fetchData: async () => {
    set({ loading: true, error: null })
    try {
      const res = await fetch('/api/lifeos')
      if (!res.ok) throw new Error('Failed to fetch data')
      const data = await res.json()
      set({ data, loading: false })
    } catch (e) {
      set({ error: (e as Error).message, loading: false })
    }
  }
}))

// Helper to convert LifeOS data to graph nodes
export function dataToNodes(data: LifeOSData): GraphNode[] {
  const nodes: GraphNode[] = []
  const now = Date.now()
  const dayMs = 24 * 60 * 60 * 1000

  // Projects at center
  data.projects.forEach((project, i) => {
    const angle = (i / Math.max(data.projects.length, 1)) * Math.PI * 2
    const radius = 5
    nodes.push({
      id: project.id,
      type: 'project',
      label: project.name,
      position: [
        Math.cos(angle) * radius,
        Math.sin(angle) * radius * 0.3,
        Math.sin(angle) * radius
      ],
      color: '#00e5ff',
      size: 1.5 + (project.taskCount || 0) * 0.1,
      data: project
    })
  })

  // Tasks orbiting their projects
  data.tasks.filter(t => t.status === 'pending').forEach((task, i) => {
    const parentIndex = data.projects.findIndex(p => p.id === task.projectId)
    const parentAngle = parentIndex >= 0
      ? (parentIndex / Math.max(data.projects.length, 1)) * Math.PI * 2
      : (i / Math.max(data.tasks.length, 1)) * Math.PI * 2
    const radius = 3
    const orbitOffset = (i % 3) * 0.5

    const priorityColor = {
      high: '#ff4444',
      medium: '#ffb800',
      low: '#44ff44'
    }[task.priority] || '#888888'

    nodes.push({
      id: task.id,
      type: 'task',
      label: task.title,
      position: [
        Math.cos(parentAngle + orbitOffset) * radius,
        Math.sin(i * 0.5) * 0.5,
        Math.sin(parentAngle + orbitOffset) * radius
      ],
      color: priorityColor,
      size: 0.6,
      data: task
    })
  })

  // Timeline as flowing ribbon
  const sortedTimeline = [...data.timeline].sort(
    (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  )
  sortedTimeline.forEach((entry, i) => {
    const t = i / Math.max(sortedTimeline.length - 1, 1)
    nodes.push({
      id: entry.id,
      type: 'timeline',
      label: entry.content.slice(0, 30) + (entry.content.length > 30 ? '...' : ''),
      position: [
        -8 + t * 16, // Spread across x-axis
        Math.sin(i * 0.3) * 0.5,
        -3
      ],
      color: '#606090',
      size: 0.25,
      data: entry
    })
  })

  // Mood as ambient glow at top
  const avgMood = data.mood.reduce((sum, m) => sum + m.score, 0) / Math.max(data.mood.length, 1)
  const moodColor = avgMood > 3 ? '#44ff88' : avgMood > 2 ? '#ffb800' : '#ff4444'

  return nodes
}

export function dataToEdges(data: LifeOSData): GraphEdge[] {
  const edges: GraphEdge[] = []

  // Task -> Project edges
  data.tasks.forEach(task => {
    if (task.projectId) {
      edges.push({
        source: task.projectId,
        target: task.id,
        type: 'project-task'
      })
    }
  })

  return edges
}
