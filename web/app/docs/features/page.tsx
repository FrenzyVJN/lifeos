'use client'

import { motion } from 'framer-motion'
import { Zap, Search, Layers, TrendingUp, MessageCircle, Clock } from 'lucide-react'

const features = [
  {
    icon: <Zap size={24} />,
    title: 'AI-Powered Extraction',
    description: 'Automatically extract tasks, priorities, due dates, and projects from natural language input.',
    details: [
      'Powered by local LLM (Qwen 2.5:7B)',
      'Rule-based fallback when Ollama offline',
      'Priority: high, medium, low',
      'Recurrence: daily, weekly, weekday, weekend',
    ],
  },
  {
    icon: <Search size={24} />,
    title: 'Smart Deduplication',
    description: 'Embedding-based matching prevents duplicate tasks. "math test" correctly matches "maths exam".',
    details: [
      'Uses all-MiniLM-L6-v2 embeddings',
      'Cosine similarity threshold: 0.82',
      'Synonym-aware normalization',
      'Updates existing task instead of creating',
    ],
  },
  {
    icon: <Layers size={24} />,
    title: 'Auto Projects',
    description: 'Tasks are automatically linked to project contexts based on detected keywords.',
    details: [
      'Auto-detect project name from input',
      'Link tasks to projects seamlessly',
      'View tasks grouped by project',
      'Track project activity over time',
    ],
  },
  {
    icon: <Clock size={24} />,
    title: 'Timeline History',
    description: 'Everything logged to a timestamped timeline. Search and explore your entire history.',
    details: [
      'Chronological log of all entries',
      'Semantic search across timeline',
      'Filter by date range',
      'Never lose context',
    ],
  },
  {
    icon: <TrendingUp size={24} />,
    title: 'Mood & Energy Tracking',
    description: 'Track how you feel over time. Get insights into your energy patterns.',
    details: [
      'Log mood with natural language',
      'AI scores mood 1-5',
      '7-day mood history chart',
      'Weekly mood averages',
    ],
  },
  {
    icon: <MessageCircle size={24} />,
    title: 'Chat With Your Data',
    description: 'Ask natural language questions about your activity and get intelligent answers.',
    details: [
      'Query tasks, projects, timeline',
      'Get overdue task alerts',
      'Weekly progress summaries',
      'Context-aware responses',
    ],
  },
]

export default function FeaturesPage() {
  return (
    <div>
      <div className="badge" style={{ marginBottom: '20px' }}>Features</div>
      <h1 style={{
        fontSize: 'clamp(36px, 5vw, 48px)',
        fontFamily: 'Syne, sans-serif',
        marginBottom: '20px',
      }}>
        Features Overview
      </h1>
      <p style={{
        color: 'var(--text-secondary)',
        fontSize: '18px',
        lineHeight: 1.8,
        marginBottom: '48px',
        maxWidth: '650px',
      }}>
        Everything LifeOS offers to help you stay organized and productive.
      </p>

      <div style={{ display: 'grid', gap: '32px' }}>
        {features.map((feature, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: i * 0.08 }}
            style={{
              padding: '32px',
              background: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              borderRadius: '16px',
            }}
          >
            <div style={{ display: 'flex', gap: '24px' }}>
              <div style={{
                width: '56px',
                height: '56px',
                background: 'var(--accent-cyan-dim)',
                borderRadius: '14px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--accent-cyan)',
                flexShrink: 0,
              }}>
                {feature.icon}
              </div>
              <div style={{ flex: 1 }}>
                <h3 style={{
                  fontSize: '22px',
                  fontFamily: 'Syne, sans-serif',
                  marginBottom: '8px',
                }}>
                  {feature.title}
                </h3>
                <p style={{
                  color: 'var(--text-secondary)',
                  fontSize: '15px',
                  lineHeight: 1.7,
                  marginBottom: '20px',
                }}>
                  {feature.description}
                </p>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                  gap: '8px',
                }}>
                  {feature.details.map((detail, j) => (
                    <div
                      key={j}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        fontSize: '13px',
                        color: 'var(--text-secondary)',
                      }}
                    >
                      <span style={{ color: 'var(--accent-cyan)' }}>✓</span>
                      {detail}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}