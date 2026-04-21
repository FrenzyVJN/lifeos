export interface Project {
  id: string
  name: string
  lastActive: string | null
  status: string
  taskCount?: number
}

export interface Task {
  id: string
  title: string
  normalizedTitle: string
  dueDate: string | null
  status: string
  priority: string
  recurrence: string | null
  nextDue: string | null
  projectId: string | null
  createdAt: string
  updatedAt: string
}

export interface TimelineEntry {
  id: string
  content: string
  timestamp: string
}

export interface MoodEntry {
  id: string
  mood: string
  score: number
  timestamp: string
}

export interface Stats {
  totalTasks: number
  pendingTasks: number
  completedTasks: number
  currentStreak: number
  avgMood7Days: number
  activeProjects: number
}

export interface LifeOSData {
  projects: Project[]
  tasks: Task[]
  timeline: TimelineEntry[]
  mood: MoodEntry[]
  stats: Stats
}

export interface GraphNode {
  id: string
  type: 'project' | 'task' | 'timeline' | 'mood'
  label: string
  position: [number, number, number]
  color: string
  size: number
  data: Project | Task | TimelineEntry | MoodEntry
}

export interface GraphEdge {
  source: string
  target: string
  type: 'project-task' | 'timeline-flow'
}
