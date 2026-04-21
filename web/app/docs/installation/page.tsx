'use client'

import { motion } from 'framer-motion'
import { CheckCircle, Terminal, HardDrive, Cpu } from 'lucide-react'
import Link from 'next/link'

const installSteps = [
  {
    title: 'System Requirements',
    items: [
      { label: 'Python', value: '3.11 or higher' },
      { label: 'Operating System', value: 'macOS, Linux, Windows (WSL)' },
      { label: 'Disk Space', value: '~500MB for Ollama models' },
      { label: 'RAM', value: '8GB minimum (16GB recommended)' },
    ],
  },
  {
    title: 'Install Ollama',
    items: [
      { label: 'macOS', value: 'brew install ollama' },
      { label: 'Linux', value: 'curl -fsSL https://ollama.com/install.sh | sh' },
      { label: 'Windows', value: 'Download from ollama.com (WSL recommended)' },
      { label: 'Manual', value: 'Download binary from github.com/ollama/ollama' },
    ],
  },
  {
    title: 'Pull the Model',
    items: [
      { label: 'Command', value: 'ollama pull qwen3.5:2b' },
      { label: 'Size', value: '~4GB download' },
      { label: 'Time', value: 'Depends on internet speed' },
    ],
  },
  {
    title: 'Install LifeOS',
    items: [
      { label: 'Clone', value: 'git clone https://github.com/FrenzyVJN/lifeos.git' },
      { label: 'Navigate', value: 'cd lifeos' },
      { label: 'Install', value: 'pip install -e .' },
      { label: 'Verify', value: 'life --version' },
    ],
  },
]

export default function InstallationPage() {
  return (
    <div>
      <div className="badge" style={{ marginBottom: '20px' }}>Installation</div>
      <h1 style={{
        fontSize: 'clamp(36px, 5vw, 48px)',
        fontFamily: 'Syne, sans-serif',
        marginBottom: '20px',
      }}>
        Installation Guide
      </h1>
      <p style={{
        color: 'var(--text-secondary)',
        fontSize: '18px',
        lineHeight: 1.8,
        marginBottom: '48px',
        maxWidth: '650px',
      }}>
        Complete installation instructions for LifeOS and all its dependencies.
      </p>

      <div style={{ display: 'grid', gap: '32px' }}>
        {installSteps.map((section, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: i * 0.1 }}
            style={{
              padding: '28px',
              background: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              borderRadius: '16px',
            }}
          >
            <h3 style={{
              fontSize: '18px',
              fontFamily: 'Syne, sans-serif',
              marginBottom: '20px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
            }}>
              <span style={{
                width: '28px',
                height: '28px',
                background: 'var(--accent-cyan-dim)',
                borderRadius: '6px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--accent-cyan)',
                fontSize: '12px',
                fontWeight: 700,
              }}>
                {i + 1}
              </span>
              {section.title}
            </h3>
            <div style={{ display: 'grid', gap: '12px' }}>
              {section.items.map((item, j) => (
                <div
                  key={j}
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '140px 1fr',
                    gap: '16px',
                    padding: '12px 16px',
                    background: 'var(--bg-secondary)',
                    borderRadius: '8px',
                  }}
                >
                  <span style={{ color: 'var(--text-dim)', fontSize: '14px' }}>{item.label}</span>
                  <code style={{
                    color: 'var(--accent-cyan)',
                    fontFamily: 'IBM Plex Mono, monospace',
                    fontSize: '13px',
                  }}>
                    {item.value}
                  </code>
                </div>
              ))}
            </div>
          </motion.div>
        ))}
      </div>

      <div style={{
        marginTop: '48px',
        padding: '32px',
        background: 'var(--bg-secondary)',
        borderRadius: '12px',
        border: '1px solid var(--border-color)',
        textAlign: 'center',
      }}>
        <CheckCircle size={32} style={{ color: 'var(--accent-cyan)', marginBottom: '16px' }} />
        <h3 style={{ fontSize: '20px', fontFamily: 'Syne, sans-serif', marginBottom: '12px' }}>
          Installation Complete
        </h3>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
          You're ready to start using LifeOS. Check out the Quickstart guide to begin.
        </p>
        <Link href="/docs/quickstart" className="btn btn-primary">
          Go to Quickstart
        </Link>
      </div>
    </div>
  )
}