'use client'

import { useGraphStore } from '@/lib/store'
import { motion } from 'framer-motion'
import {
  Brain,
  Layers,
  CheckCircle2,
  Circle,
  Calendar,
  TrendingUp,
  Flame,
  Smile,
  RotateCcw,
  ZoomIn,
  ZoomOut
} from 'lucide-react'

export default function GraphUI() {
  const { data, loading, error, viewMode, setViewMode, selectedNode, hoveredNode } = useGraphStore()

  if (loading) {
    return (
      <div style={{
        position: 'absolute',
        top: 20,
        left: 20,
        background: 'rgba(20, 20, 32, 0.95)',
        border: '1px solid rgba(0, 229, 255, 0.2)',
        borderRadius: 16,
        padding: 32,
        color: '#00e5ff',
        backdropFilter: 'blur(20px)',
        zIndex: 100
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <RotateCcw size={20} className="animate-spin" />
          <span>Loading LifeOS data...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div style={{
        position: 'absolute',
        top: 20,
        left: 20,
        background: 'rgba(20, 20, 32, 0.95)',
        border: '1px solid rgba(255, 68, 68, 0.3)',
        borderRadius: 16,
        padding: 24,
        color: '#ff4444',
        backdropFilter: 'blur(20px)',
        zIndex: 100
      }}>
        Error: {error}
      </div>
    )
  }

  if (!data) return null

  const stats = data.stats

  return (
    <>
      {/* Stats Panel */}
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        style={{
          position: 'absolute',
          top: 20,
          left: 20,
          background: 'rgba(20, 20, 32, 0.9)',
          border: '1px solid rgba(0, 229, 255, 0.2)',
          borderRadius: 16,
          padding: 24,
          backdropFilter: 'blur(20px)',
          zIndex: 100,
          minWidth: 200
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
          <Brain size={24} style={{ color: '#00e5ff' }} />
          <span style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: 18, color: '#f0f0f5' }}>
            LifeOS
          </span>
        </div>

        <div style={{ display: 'grid', gap: 16 }}>
          <StatRow
            icon={<Layers size={16} />}
            label="Projects"
            value={stats.activeProjects}
            color="#00e5ff"
          />
          <StatRow
            icon={<Circle size={16} />}
            label="Pending"
            value={stats.pendingTasks}
            color="#ffb800"
          />
          <StatRow
            icon={<CheckCircle2 size={16} />}
            label="Completed"
            value={stats.completedTasks}
            color="#44ff44"
          />
          <StatRow
            icon={<Flame size={16} />}
            label="Streak"
            value={`${stats.currentStreak} days`}
            color="#ff6b35"
          />
          <StatRow
            icon={<Smile size={16} />}
            label="Avg Mood"
            value={`${stats.avgMood7Days}/5`}
            color={stats.avgMood7Days > 3 ? '#44ff88' : stats.avgMood7Days > 2 ? '#ffb800' : '#ff4444'}
          />
        </div>
      </motion.div>

      {/* View Mode Toggle */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        style={{
          position: 'absolute',
          top: 20,
          left: '50%',
          transform: 'translateX(-50%)',
          display: 'flex',
          gap: 8,
          background: 'rgba(20, 20, 32, 0.9)',
          border: '1px solid rgba(0, 229, 255, 0.2)',
          borderRadius: 100,
          padding: 8,
          backdropFilter: 'blur(20px)',
          zIndex: 100
        }}
      >
        {(['all', 'projects', 'tasks', 'timeline'] as const).map(mode => (
          <button
            key={mode}
            onClick={() => setViewMode(mode)}
            style={{
              padding: '8px 16px',
              borderRadius: 100,
              border: 'none',
              background: viewMode === mode ? '#00e5ff' : 'transparent',
              color: viewMode === mode ? '#0a0a0f' : '#9090a0',
              fontFamily: 'Syne, sans-serif',
              fontWeight: 600,
              fontSize: 13,
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            {mode.charAt(0).toUpperCase() + mode.slice(1)}
          </button>
        ))}
      </motion.div>

      {/* Selected/Hovered Node Info */}
      {(() => {
        const node = selectedNode || hoveredNode
        if (!node) return null
        return (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            style={{
              position: 'absolute',
              top: 20,
              right: 20,
              background: 'rgba(20, 20, 32, 0.9)',
              border: '1px solid rgba(0, 229, 255, 0.3)',
              borderRadius: 16,
              padding: 20,
              backdropFilter: 'blur(20px)',
              zIndex: 100,
              maxWidth: 300
            }}
          >
            <div style={{
              fontFamily: 'Syne, sans-serif',
              fontWeight: 700,
              fontSize: 14,
              color: node.color || '#00e5ff',
              textTransform: 'uppercase',
              letterSpacing: 1,
              marginBottom: 8
            }}>
              {node.type}
            </div>
            <div style={{
              fontFamily: 'IBM Plex Sans, sans-serif',
              fontSize: 16,
              color: '#f0f0f5',
              marginBottom: 8
            }}>
              {node.label}
            </div>
            {node.type === 'task' && 'priority' in node.data && (
              <div style={{ fontSize: 12, color: '#9090a0' }}>
                Priority: {node.data.priority}
                {'dueDate' in node.data && node.data.dueDate && (
                  <> • Due: {new Date(node.data.dueDate).toLocaleDateString()}</>
                )}
              </div>
            )}
          </motion.div>
        )
      })()}

      {/* Controls Help */}
      <div style={{
        position: 'absolute',
        bottom: 20,
        left: '50%',
        transform: 'translateX(-50%)',
        display: 'flex',
        gap: 24,
        background: 'rgba(20, 20, 32, 0.7)',
        border: '1px solid rgba(0, 229, 255, 0.1)',
        borderRadius: 100,
        padding: '12px 24px',
        backdropFilter: 'blur(10px)',
        zIndex: 100
      }}>
        <ControlHint icon="🖱️" text="Drag to rotate" />
        <ControlHint icon="⚙️" text="Scroll to zoom" />
        <ControlHint icon="📌" text="Click node for details" />
      </div>
    </>
  )
}

function StatRow({ icon, label, value, color }: {
  icon: React.ReactNode
  label: string
  value: string | number
  color: string
}) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
      <div style={{ color }}>{icon}</div>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 11, color: '#606070', textTransform: 'uppercase', letterSpacing: 0.5 }}>
          {label}
        </div>
        <div style={{ fontSize: 18, fontWeight: 600, color: '#f0f0f5', fontFamily: 'Syne, sans-serif' }}>
          {value}
        </div>
      </div>
    </div>
  )
}

function ControlHint({ icon, text }: { icon: string; text: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#606070', fontSize: 12 }}>
      <span>{icon}</span>
      <span>{text}</span>
    </div>
  )
}
