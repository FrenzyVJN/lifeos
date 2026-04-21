'use client'

import { motion } from 'framer-motion'
import { Code, Terminal, Zap, CheckCircle, AlertCircle } from 'lucide-react'
import Link from 'next/link'

const commands = [
  { command: 'life log "text"', description: 'Log a thought with automatic task extraction' },
  { command: 'life tasks', description: 'View all pending tasks' },
  { command: 'life tasks --done', description: 'View completed tasks' },
  { command: 'life tasks --high', description: 'View high priority tasks only' },
  { command: 'life tasks --today', description: 'View tasks due today or overdue' },
  { command: 'life done <id>', description: 'Mark a task as complete' },
  { command: 'life timeline', description: 'View full chronological log' },
  { command: 'life projects', description: 'List all active projects' },
  { command: 'life project <id>', description: 'View tasks for a specific project' },
  { command: 'life edit <id> --title "..."', description: 'Update task title' },
  { command: 'life edit <id> --due "..."', description: 'Update task due date' },
  { command: 'life delete <id>', description: 'Soft-delete a task' },
  { command: 'life summary', description: "Today's summary with streak, mood, tasks" },
  { command: 'life digest', description: 'AI-generated daily digest' },
  { command: 'life weekly', description: '7-day summary with stats' },
  { command: 'life search "query"', description: 'Semantic search across all data' },
  { command: 'life streak', description: 'View consecutive logging days' },
  { command: 'life mood "feeling..."', description: 'Log mood with AI scoring' },
  { command: 'life mood-history', description: 'View 7-day mood chart' },
  { command: 'life report', description: 'Generate markdown report' },
  { command: 'life report --week', description: 'Generate weekly report' },
  { command: 'life report --out file.md', description: 'Export report to file' },
  { command: 'life chat "question"', description: 'Natural language Q&A about your data' },
]

export default function CommandsPage() {
  return (
    <div>
      <div className="badge" style={{ marginBottom: '20px' }}>Reference</div>
      <h1 style={{
        fontSize: 'clamp(36px, 5vw, 48px)',
        fontFamily: 'Syne, sans-serif',
        marginBottom: '20px',
      }}>
        Commands
      </h1>
      <p style={{
        color: 'var(--text-secondary)',
        fontSize: '18px',
        lineHeight: 1.8,
        marginBottom: '48px',
        maxWidth: '650px',
      }}>
        Complete reference of all available LifeOS commands.
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {commands.map((cmd, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4, delay: i * 0.03 }}
            style={{
              display: 'grid',
              gridTemplateColumns: '1fr 2fr',
              gap: '24px',
              padding: '20px 24px',
              background: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              borderRadius: '12px',
              alignItems: 'center',
              transition: 'all 0.2s ease',
            }}
          >
            <code style={{
              fontFamily: 'IBM Plex Mono, monospace',
              fontSize: '14px',
              color: 'var(--accent-cyan)',
              background: 'var(--bg-secondary)',
              padding: '10px 14px',
              borderRadius: '6px',
            }}>
              {cmd.command}
            </code>
            <span style={{ color: 'var(--text-secondary)', fontSize: '15px' }}>
              {cmd.description}
            </span>
          </motion.div>
        ))}
      </div>

      <div style={{
        marginTop: '48px',
        padding: '24px',
        background: 'var(--bg-secondary)',
        borderRadius: '12px',
        border: '1px solid var(--border-color)',
      }}>
        <h3 style={{
          fontSize: '16px',
          fontFamily: 'Syne, sans-serif',
          marginBottom: '16px',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
        }}>
          <AlertCircle size={18} style={{ color: 'var(--accent-amber)' }} />
          Pro Tip
        </h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px', lineHeight: 1.7 }}>
          Use <code style={{ color: 'var(--accent-cyan)', fontFamily: 'IBM Plex Mono, monospace' }}>life --help</code> to see all available commands
          at any time. Most commands have sub-options you can explore.
        </p>
      </div>
    </div>
  )
}