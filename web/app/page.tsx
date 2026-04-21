'use client'

import { motion } from 'framer-motion'
import { Brain, Zap, Clock, Layers, TrendingUp, Search, MessageCircle } from 'lucide-react'
import { useState, useEffect } from 'react'
import Link from 'next/link'

function TerminalAnimation() {
  const [currentLine, setCurrentLine] = useState(0)

  const lines = [
    { text: '~ » life log "worked on backend, math test in 3 days"', type: 'input' },
    { text: 'Logged: worked on backend, math test in 3 days', type: 'log' },
    { text: 'Task created: math test (due: Apr 17, 2026)', type: 'task' },
    { text: 'Project: LifeOS (linked)', type: 'project' },
    { text: '', type: 'empty' },
    { text: '~ » life log "standup meeting every weekday"', type: 'input' },
    { text: 'Task created: standup meeting (recurring: weekday)', type: 'task' },
    { text: '', type: 'empty' },
    { text: '~ » life mood "productive and focused"', type: 'input' },
    { text: 'Mood logged: productive and focused (4/5)', type: 'project' },
  ]

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentLine((prev) => (prev + 1) % (lines.length + 5))
    }, 1200)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="terminal-window" style={{ width: '100%', maxWidth: '550px' }}>
      <div className="terminal-header">
        <div className="terminal-dot dot-red" />
        <div className="terminal-dot dot-yellow" />
        <div className="terminal-dot dot-green" />
        <span style={{ marginLeft: '12px', color: 'var(--text-dim)', fontSize: '12px' }}>
          lifeos — bash
        </span>
      </div>
      <div className="terminal-body">
        {lines.slice(0, Math.min(currentLine, lines.length)).map((line, i) => {
          let color = 'var(--text-primary)'
          if (line.type === 'log') color = 'var(--text-secondary)'
          if (line.type === 'task') color = 'var(--accent-cyan)'
          if (line.type === 'project') color = 'var(--accent-amber)'
          return (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3 }}
              style={{ color, marginBottom: '4px' }}
            >
              {line.text || '\u00A0'}
            </motion.div>
          )
        })}
        {currentLine <= lines.length && (
          <span style={{ color: 'var(--accent-cyan)' }}>▋</span>
        )}
      </div>
    </div>
  )
}

function FloatingOrb({ className, delay = 0 }: { className: string; delay?: number }) {
  return (
    <motion.div
      className={`orb ${className}`}
      animate={{ y: [0, -30, 0], x: [0, 15, 0] }}
      transition={{ duration: 8, repeat: Infinity, delay, ease: 'easeInOut' }}
    />
  )
}

export default function Home() {
  const features = [
    {
      icon: <Zap size={24} />,
      title: 'AI-Powered Extraction',
      description: 'Tasks, projects, priorities, and due dates are parsed automatically using local LLM.',
    },
    {
      icon: <Search size={24} />,
      title: 'Smart Deduplication',
      description: 'Embedding-based matching prevents duplicates. "math test" matches "maths exam" correctly.',
    },
    {
      icon: <Clock size={24} />,
      title: 'Timeline History',
      description: 'Everything logged to a timestamped timeline. Search and explore your entire history.',
    },
    {
      icon: <Layers size={24} />,
      title: 'Auto Projects',
      description: 'Tasks are automatically linked to project contexts. View by project or explore all.',
    },
    {
      icon: <TrendingUp size={24} />,
      title: 'Mood & Energy',
      description: 'Track how you feel over time. Weekly mood charts and energy level insights.',
    },
    {
      icon: <MessageCircle size={24} />,
      title: 'Chat With Your Data',
      description: 'Ask natural language questions about your activity and get intelligent answers.',
    },
  ]

  const steps = [
    { number: '01', title: 'Log Your Thought', description: "Type what's on your mind. LifeOS extracts tasks and organizes everything." },
    { number: '02', title: 'AI Extracts & Organizes', description: 'Tasks, projects, priorities, and due dates detected automatically.' },
    { number: '03', title: 'Stay In Flow', description: 'View tasks, track progress, get AI summaries without leaving your terminal.' },
  ]

  return (
    <main style={{ minHeight: '100vh' }}>
      <nav className="nav">
        <Link href="/" className="nav-logo" style={{ textDecoration: 'none' }}>
          <Brain size={28} style={{ color: 'var(--accent-cyan)' }} />
          Life<span>OS</span>
        </Link>
        <div className="nav-links">
          <Link href="/docs">Docs</Link>
          <Link href="/graph">Graph</Link>
          <a href="#features">Features</a>
          <a href="#how-it-works">How It Works</a>
          <a href="#pricing">Pricing</a>
        </div>
        <Link href="/docs/quickstart" className="nav-cta">Get Started</Link>
      </nav>

      <section className="section" style={{ paddingTop: '180px', textAlign: 'center', position: 'relative', overflow: 'hidden' }}>
        <div className="grid-bg" />
        <FloatingOrb className="orb-cyan" delay={0} />
        <FloatingOrb className="orb-amber" delay={2} />
        <div className="container" style={{ position: 'relative', zIndex: 1 }}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
            <div className="badge" style={{ marginBottom: '32px' }}>
              <Zap size={14} />
              Privacy-First | Local-First | No Cloud
            </div>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.1 }}
            style={{
              fontSize: 'clamp(48px, 8vw, 80px)',
              fontWeight: 800,
              marginBottom: '24px',
              background: 'linear-gradient(135deg, var(--text-primary) 0%, var(--accent-cyan) 50%, var(--accent-amber) 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}
          >
            Your Second Brain,
            <br />
            In The Terminal.
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            style={{ fontSize: '20px', color: 'var(--text-secondary)', maxWidth: '600px', margin: '0 auto 48px', lineHeight: 1.8 }}
          >
            Dump your thoughts in natural language. LifeOS automatically extracts tasks,
            organizes projects, and generates insights — all running locally on your machine.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}
          >
            <Link href="/docs/quickstart" className="btn btn-primary" style={{ fontSize: '16px', padding: '16px 32px' }}>
              <Zap size={18} />
              Start Free
            </Link>
            <a href="#how-it-works" className="btn btn-secondary" style={{ fontSize: '16px', padding: '16px 32px' }}>
              See How It Works
            </a>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 60, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            style={{ marginTop: '80px', display: 'flex', justifyContent: 'center' }}
          >
            <TerminalAnimation />
          </motion.div>
        </div>
      </section>

      <section id="features" className="section" style={{ background: 'var(--bg-secondary)' }}>
        <div className="container">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <span className="badge" style={{ marginBottom: '20px' }}>Features</span>
          </motion.div>
          <motion.h2
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            style={{ fontSize: 'clamp(36px, 5vw, 56px)', marginBottom: '20px' }}
          >
            Everything you need.
            <br />
            <span style={{ color: 'var(--accent-cyan)' }}>Nothing you don&apos;t.</span>
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            style={{ color: 'var(--text-secondary)', fontSize: '18px', maxWidth: '500px', margin: '0 auto' }}
          >
            Built for developers who want power without complexity. All your data stays on your machine.
          </motion.p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px' }}>
            {features.map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                className="card"
              >
                <div className="feature-icon">{feature.icon}</div>
                <h3 style={{ fontSize: '20px', marginBottom: '12px', fontFamily: 'Syne, sans-serif' }}>{feature.title}</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '15px', lineHeight: 1.7 }}>{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <section id="how-it-works" className="section" style={{ position: 'relative', overflow: 'hidden' }}>
        <div className="grid-bg" />
        <div className="container" style={{ position: 'relative', zIndex: 1 }}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            style={{ textAlign: 'center', marginBottom: '80px' }}
          >
            <span className="badge">How It Works</span>
            <h2 style={{ fontSize: 'clamp(36px, 5vw, 56px)', marginTop: '24px' }}>
              Three steps to
              <br />
              <span style={{ color: 'var(--accent-amber)' }}>productivity nirvana</span>
            </h2>
          </motion.div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '40px' }}>
            {steps.map((step, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -40 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: i * 0.2 }}
                style={{ textAlign: 'center' }}
              >
                <div style={{
                  width: '80px',
                  height: '80px',
                  background: 'var(--bg-card)',
                  border: '2px solid var(--accent-cyan)',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 24px',
                  fontFamily: 'Syne, sans-serif',
                  fontSize: '24px',
                  fontWeight: 700,
                  color: 'var(--accent-cyan)',
                  boxShadow: 'var(--glow-cyan)',
                }}>
                  {step.number}
                </div>
                <h3 style={{ fontSize: '22px', marginBottom: '12px', fontFamily: 'Syne, sans-serif' }}>{step.title}</h3>
                <p style={{ color: 'var(--text-secondary)', lineHeight: 1.7 }}>{step.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <section className="section" style={{ background: 'var(--bg-secondary)' }}>
        <div className="container">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '60px', alignItems: 'center' }}>
            <motion.div
              initial={{ opacity: 0, x: -40 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <span className="badge" style={{ marginBottom: '20px' }}>Simple Yet Powerful</span>
              <h2 style={{ fontSize: 'clamp(32px, 4vw, 48px)', marginBottom: '24px' }}>
                One command.
                <br />
                <span style={{ color: 'var(--accent-cyan)' }}>Infinite possibilities.</span>
              </h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '17px', lineHeight: 1.8, marginBottom: '32px' }}>
                Type naturally. Get organized. No learning curve, no complex menus.
                Just type what&apos;s on your mind and let the AI do the rest.
              </p>
              <div className="code-block" style={{ padding: '24px' }}>
                <div><span style={{ color: 'var(--text-dim)' }}># Log a thought with automatic task extraction</span></div>
                <div style={{ marginTop: '12px' }}>life log <span style={{ color: 'var(--accent-amber)' }}>"study for math exam next week"</span></div>
                <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid var(--border-color)' }}>
                  <div><span style={{ color: 'var(--accent-cyan)' }}>&#x2713;</span> <span>Task created: study for math exam</span></div>
                  <div><span style={{ color: 'var(--accent-amber)' }}>&#x2192;</span> <span>Project: Education</span></div>
                  <div><span style={{ color: 'var(--text-dim)' }}>&#x2192;</span> <span>Due: Apr 21, 2026</span></div>
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 40 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.2 }}
              style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}
            >
              {[
                'View tasks with `life tasks`',
                'Get daily digests with `life digest`',
                'Track mood with `life mood`',
                'Search everything with `life search`',
                'Export reports with `life report`',
              ].map((cmd, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: 20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: 0.3 + i * 0.1 }}
                  className="code-block"
                  style={{ display: 'flex', alignItems: 'center', gap: '16px', padding: '16px 20px' }}
                >
                  <span style={{ color: 'var(--accent-cyan)', fontWeight: 600 }}>&#x2192;</span>
                  <span>{cmd}</span>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </div>
      </section>

      <section id="pricing" className="section" style={{ position: 'relative' }}>
        <div className="container">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            style={{ textAlign: 'center', marginBottom: '64px' }}
          >
            <span className="badge">Pricing</span>
            <h2 style={{ fontSize: 'clamp(36px, 5vw, 56px)', marginTop: '24px' }}>
              Simple pricing.
              <br />
              <span style={{ color: 'var(--accent-amber)' }}>No surprises.</span>
            </h2>
          </motion.div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '32px', maxWidth: '900px', margin: '0 auto' }}>
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5 }}
              className="card"
              style={{ textAlign: 'center' }}
            >
              <div style={{ width: '64px', height: '64px', background: 'var(--accent-cyan-dim)', borderRadius: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 24px', color: 'var(--accent-cyan)' }}>
                <Brain size={32} />
              </div>
              <h3 style={{ fontSize: '28px', marginBottom: '8px', fontFamily: 'Syne, sans-serif' }}>Free</h3>
              <div style={{ fontSize: '48px', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '24px', fontFamily: 'Syne, sans-serif' }}>
                $0<span style={{ fontSize: '18px', color: 'var(--text-secondary)', fontWeight: 400 }}>/mo</span>
              </div>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '32px' }}>For developers who want full control</p>
              <ul style={{ listStyle: 'none', textAlign: 'left', marginBottom: '32px' }}>
                {['CLI tool (current)', 'Unlimited tasks', 'Timeline history', 'Project management', 'Mood tracking', 'Local LLM inference'].map((feature, i) => (
                  <li key={i} style={{ padding: '10px 0', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: '12px', color: 'var(--text-secondary)' }}>
                    <span style={{ color: 'var(--accent-cyan)' }}>&#x2713;</span>
                    {feature}
                  </li>
                ))}
              </ul>
              <button className="btn btn-secondary" style={{ width: '100%' }}>Download CLI</button>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="card"
              style={{ textAlign: 'center', border: '2px solid var(--accent-amber)', position: 'relative', overflow: 'hidden' }}
            >
              <div style={{ position: 'absolute', top: '20px', right: '-35px', background: 'var(--accent-amber)', color: 'var(--bg-primary)', padding: '6px 40px', fontSize: '11px', fontWeight: 700, transform: 'rotate(45deg)', textTransform: 'uppercase', letterSpacing: '1px' }}>
                Coming Soon
              </div>
              <div style={{ width: '64px', height: '64px', background: 'var(--accent-amber-dim)', borderRadius: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 24px', color: 'var(--accent-amber)' }}>
                <Layers size={32} />
              </div>
              <h3 style={{ fontSize: '28px', marginBottom: '8px', fontFamily: 'Syne, sans-serif' }}>Pro</h3>
              <div style={{ fontSize: '48px', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '24px', fontFamily: 'Syne, sans-serif' }}>
                TBD<span style={{ fontSize: '18px', color: 'var(--text-secondary)', fontWeight: 400 }}>/mo</span>
              </div>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '32px' }}>For teams and power users</p>
              <ul style={{ listStyle: 'none', textAlign: 'left', marginBottom: '32px' }}>
                {['Everything in Free', 'Web UI (coming soon)', 'Mobile app (coming soon)', 'Cloud sync (optional)', 'Team collaboration', 'Priority support'].map((feature, i) => (
                  <li key={i} style={{ padding: '10px 0', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: '12px', color: 'var(--text-secondary)' }}>
                    <span style={{ color: 'var(--accent-amber)' }}>&#x2713;</span>
                    {feature}
                  </li>
                ))}
              </ul>
              <button className="btn btn-primary" style={{ width: '100%', opacity: 0.6, cursor: 'not-allowed' }}>Join Waitlist</button>
            </motion.div>
          </div>
        </div>
      </section>

      <section className="section" style={{ background: 'linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%)', textAlign: 'center' }}>
        <div className="container">
          <motion.div initial={{ opacity: 0, y: 40 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}>
            <h2 style={{ fontSize: 'clamp(36px, 5vw, 56px)', marginBottom: '24px' }}>
              Ready to take control
              <br />
              <span style={{ color: 'var(--accent-cyan)' }}>of your productivity?</span>
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '18px', maxWidth: '500px', margin: '0 auto 40px' }}>
              Join thousands of developers who&apos;ve replaced their scattered notes,
              task managers, and productivity apps with LifeOS.
            </p>
            <Link href="/docs/quickstart" className="btn btn-primary" style={{ fontSize: '16px', padding: '18px 40px' }}>
              <Zap size={20} />
              Get Started — It&apos;s Free
            </Link>
          </motion.div>
        </div>
      </section>

      <footer className="footer">
        <div className="container">
          <div className="footer-logo">
            <Brain size={24} style={{ color: 'var(--accent-cyan)', marginRight: '8px' }} />
            Life<span>OS</span>
          </div>
          <p style={{ marginBottom: '12px' }}>Your second brain, in the terminal.</p>
          <p style={{ fontSize: '13px' }}>© 2026 LifeOS. Open source under MIT License.</p>
        </div>
      </footer>
    </main>
  )
}