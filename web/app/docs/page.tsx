'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { Book, Zap, Code, MessageCircle, Layers, TrendingUp, Search } from 'lucide-react'

const sections = [
  {
    title: 'Getting Started',
    items: [
      { href: '/docs/quickstart', title: 'Quickstart', description: 'Get up and running in 5 minutes', icon: <Zap size={20} /> },
      { href: '/docs/installation', title: 'Installation', description: 'Full installation guide', icon: <Code size={20} /> },
    ],
  },
  {
    title: 'Core Concepts',
    items: [
      { href: '/docs/commands', title: 'Commands', description: 'All available commands', icon: <Book size={20} /> },
      { href: '/docs/features', title: 'Features', description: 'Explore all features', icon: <Layers size={20} /> },
    ],
  },
  {
    title: 'Advanced',
    items: [
      { href: '/docs/chat', title: 'Chat Interface', description: 'Natural language queries', icon: <MessageCircle size={20} /> },
    ],
  },
]

const featureCards = [
  { title: 'Smart Extraction', desc: 'AI-powered task extraction from natural language', icon: <Zap size={24} /> },
  { title: 'Semantic Search', desc: 'Find anything using embedding-based search', icon: <Search size={24} /> },
  { title: 'Mood Tracking', desc: 'Track your energy and mood over time', icon: <TrendingUp size={24} /> },
]

export default function DocsPage() {
  return (
    <div>
      <div className="badge" style={{ marginBottom: '20px' }}>Documentation</div>
      <h1 style={{
        fontSize: 'clamp(36px, 5vw, 48px)',
        fontFamily: 'Syne, sans-serif',
        marginBottom: '20px',
      }}>
        LifeOS Documentation
      </h1>
      <p style={{
        color: 'var(--text-secondary)',
        fontSize: '18px',
        lineHeight: 1.8,
        marginBottom: '48px',
        maxWidth: '600px',
      }}>
        Everything you need to know about LifeOS. From quick installation to advanced features.
      </p>

      {/* Sections Grid */}
      <div style={{ display: 'grid', gap: '48px', marginBottom: '64px' }}>
        {sections.map((section, i) => (
          <div key={i}>
            <h2 style={{
              fontSize: '14px',
              textTransform: 'uppercase',
              letterSpacing: '1px',
              color: 'var(--text-dim)',
              marginBottom: '16px',
            }}>
              {section.title}
            </h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
              {section.items.map((item, j) => (
                <Link
                  key={j}
                  href={item.href}
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '16px',
                    padding: '20px',
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '12px',
                    textDecoration: 'none',
                    transition: 'all 0.3s ease',
                  }}
                >
                  <div style={{
                    width: '40px',
                    height: '40px',
                    background: 'var(--accent-cyan-dim)',
                    borderRadius: '10px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'var(--accent-cyan)',
                    flexShrink: 0,
                  }}>
                    {item.icon}
                  </div>
                  <div>
                    <h3 style={{
                      fontSize: '16px',
                      fontFamily: 'Syne, sans-serif',
                      marginBottom: '4px',
                      color: 'var(--text-primary)',
                    }}>
                      {item.title}
                    </h3>
                    <p style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
                      {item.description}
                    </p>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Feature Cards */}
      <div style={{
        padding: '40px',
        background: 'var(--bg-secondary)',
        borderRadius: '16px',
        border: '1px solid var(--border-color)',
      }}>
        <h2 style={{
          fontSize: '20px',
          fontFamily: 'Syne, sans-serif',
          marginBottom: '24px',
        }}>
          Quick Links
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
          {featureCards.map((card, i) => (
            <div key={i} style={{
              padding: '20px',
              background: 'var(--bg-card)',
              borderRadius: '10px',
              border: '1px solid var(--border-color)',
            }}>
              <div style={{
                width: '40px',
                height: '40px',
                background: 'var(--accent-amber-dim)',
                borderRadius: '10px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--accent-amber)',
                marginBottom: '12px',
              }}>
                {card.icon}
              </div>
              <h3 style={{ fontSize: '14px', fontFamily: 'Syne, sans-serif', marginBottom: '4px' }}>
                {card.title}
              </h3>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                {card.desc}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}