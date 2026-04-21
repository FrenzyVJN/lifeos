'use client'

import { motion } from 'framer-motion'
import { CheckCircle, Terminal, Zap, Brain, Cloud, HardDrive } from 'lucide-react'
import Link from 'next/link'

const steps = [
  {
    title: 'Install Ollama',
    description: 'Ollama is a local LLM runtime that powers LifeOS\'s AI capabilities. Choose your platform below:',
    code: `# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows (WSL recommended)
# Install WSL first, then use the Linux install command above

# Or download directly from https://ollama.com/download`,
    icon: <Cloud size={24} />,
    color: 'cyan',
  },
  {
    title: 'Pull the Model',
    description: 'Download the Qwen 3.5 2B model. ~2.7GB - enables fast AI-powered task extraction.',
    code: `ollama pull qwen3.5:2b`,
    icon: <Brain size={24} />,
    color: 'amber',
  },
  {
    title: 'Start Ollama',
    description: 'Run Ollama in the background. It will handle all LLM requests.',
    code: `# macOS / Linux
ollama serve

# Windows (WSL)
./ollama serve

# Or run in background
ollama serve &`,
    icon: <Zap size={24} />,
    color: 'cyan',
  },
  {
    title: 'Install LifeOS',
    description: 'Clone the repo and install the package. Python 3.11+ required.',
    code: `# Clone the repository
git clone https://github.com/FrenzyVJN/lifeos.git
cd lifeos

# Install with pip (macOS / Linux / WSL)
pip install -e .

# Windows (PowerShell)
pip install -e .`,
    icon: <Terminal size={24} />,
    color: 'amber',
  },
  {
    title: 'Start Logging',
    description: 'You\'re ready! Use `life log` to capture thoughts and tasks.',
    code: `# Log a thought with automatic task extraction
life log "worked on backend, math test in 3 days"

# View your pending tasks
life tasks

# Get an AI-powered daily digest
life digest

# If 'life' command not found, ensure ~/.local/bin is in PATH
# export PATH="$HOME/.local/bin:$PATH"`,
    icon: <CheckCircle size={24} />,
    color: 'cyan',
  },
]

const requirements = [
  { name: 'Python', version: '3.11+' },
  { name: 'Ollama', version: 'Latest' },
  { name: 'Disk Space', value: '~500MB for models' },
  { name: 'Memory', value: '8GB+ recommended' },
]

export default function QuickstartPage() {
  return (
    <div>
      <div className="badge" style={{ marginBottom: '20px' }}>Quickstart</div>
      <h1 style={{
        fontSize: 'clamp(36px, 5vw, 48px)',
        fontFamily: 'Syne, sans-serif',
        marginBottom: '20px',
      }}>
        Get Started in 5 Minutes
      </h1>
      <p style={{
        color: 'var(--text-secondary)',
        fontSize: '18px',
        lineHeight: 1.8,
        marginBottom: '48px',
        maxWidth: '650px',
      }}>
        LifeOS is a local-first productivity tool. Your data never leaves your machine.
        No cloud, no subscriptions, no tracking.
      </p>

      {/* Requirements */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
        gap: '16px',
        marginBottom: '64px',
        padding: '24px',
        background: 'var(--bg-secondary)',
        borderRadius: '12px',
        border: '1px solid var(--border-color)',
      }}>
        {requirements.map((req, i) => (
          <div key={i} style={{
            textAlign: 'center',
            padding: '16px',
            background: 'var(--bg-card)',
            borderRadius: '8px',
          }}>
            <div style={{
              fontSize: '20px',
              fontFamily: 'Syne, sans-serif',
              fontWeight: 700,
              color: 'var(--accent-cyan)',
              marginBottom: '4px',
            }}>
              {req.name}
            </div>
            <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
              {req.version || req.value}
            </div>
          </div>
        ))}
      </div>

      {/* Steps */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
        {steps.map((step, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: i * 0.1 }}
            style={{
              display: 'grid',
              gridTemplateColumns: '50px 1fr',
              gap: '24px',
              padding: '32px',
              background: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              borderRadius: '16px',
              transition: 'all 0.3s ease',
            }}
          >
            <div style={{
              width: '50px',
              height: '50px',
              background: step.color === 'cyan' ? 'var(--accent-cyan-dim)' : 'var(--accent-amber-dim)',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: step.color === 'cyan' ? 'var(--accent-cyan)' : 'var(--accent-amber)',
              fontSize: '14px',
              fontFamily: 'Syne, sans-serif',
              fontWeight: 700,
            }}>
              {i + 1}
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                <div style={{
                  width: '36px',
                  height: '36px',
                  background: step.color === 'cyan' ? 'var(--accent-cyan-dim)' : 'var(--accent-amber-dim)',
                  borderRadius: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: step.color === 'cyan' ? 'var(--accent-cyan)' : 'var(--accent-amber)',
                }}>
                  {step.icon}
                </div>
                <h3 style={{
                  fontSize: '20px',
                  fontFamily: 'Syne, sans-serif',
                  fontWeight: 700,
                }}>
                  {step.title}
                </h3>
              </div>
              <p style={{
                color: 'var(--text-secondary)',
                fontSize: '15px',
                lineHeight: 1.7,
                marginBottom: '20px',
              }}>
                {step.description}
              </p>
              <div style={{
                background: 'var(--bg-secondary)',
                borderRadius: '8px',
                padding: '16px 20px',
                fontFamily: 'IBM Plex Mono, monospace',
                fontSize: '13px',
                lineHeight: 1.8,
                overflowX: 'auto',
              }}>
                {step.code.split('\n').map((line, j) => (
                  <div key={j} style={{
                    color: line.startsWith('#') ? 'var(--text-dim)' : 'var(--text-primary)',
                  }}>
                    {line || '\u00A0'}
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Next Steps */}
      <div style={{
        marginTop: '64px',
        padding: '32px',
        background: 'linear-gradient(135deg, var(--accent-cyan-dim) 0%, var(--accent-amber-dim) 100%)',
        borderRadius: '16px',
        textAlign: 'center',
      }}>
        <h2 style={{
          fontSize: '24px',
          fontFamily: 'Syne, sans-serif',
          marginBottom: '16px',
        }}>
          Ready to boost your productivity?
        </h2>
        <p style={{
          color: 'var(--text-secondary)',
          fontSize: '16px',
          marginBottom: '24px',
        }}>
          Explore all commands and features in the documentation.
        </p>
        <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link href="/docs/commands" className="btn btn-primary">
            View All Commands
          </Link>
          <Link href="/" className="btn btn-secondary" style={{ background: 'var(--bg-primary)', border: '1px solid var(--border-color)' }}>
            Back to Home
          </Link>
        </div>
      </div>
    </div>
  )
}