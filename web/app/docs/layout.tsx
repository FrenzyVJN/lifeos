'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion } from 'framer-motion'
import { Brain, Home, Zap, Book, Code, MessageCircle, Heart } from 'lucide-react'

const navItems = [
  { href: '/docs', label: 'Overview', icon: <Home size={18} /> },
  { href: '/docs/quickstart', label: 'Quickstart', icon: <Zap size={18} /> },
  { href: '/docs/installation', label: 'Installation', icon: <Code size={18} /> },
  { href: '/docs/commands', label: 'Commands', icon: <Book size={18} /> },
  { href: '/docs/features', label: 'Features', icon: <Heart size={18} /> },
  { href: '/docs/chat', label: 'Chat', icon: <MessageCircle size={18} /> },
]

export default function DocsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
    }}>
      {/* Docs Navigation */}
      <nav className="nav" style={{
        background: 'var(--bg-primary)',
        borderBottom: '1px solid var(--border-color)',
        position: 'sticky',
        top: 0,
        zIndex: 100,
      }}>
        <Link href="/" className="nav-logo" style={{ textDecoration: 'none' }}>
          <Brain size={28} style={{ color: 'var(--accent-cyan)' }} />
          Life<span>OS</span>
        </Link>
        <div className="nav-links">
          <Link href="/docs" style={{ color: pathname === '/docs' ? 'var(--text-primary)' : 'var(--text-secondary)' }}>Docs</Link>
          <a href="/#features">Features</a>
          <a href="/#pricing">Pricing</a>
        </div>
        <Link href="/docs/quickstart" className="nav-cta">
          Get Started
        </Link>
      </nav>

      <div style={{
        display: 'flex',
        flex: 1,
      }}>
        {/* Sidebar */}
        <aside style={{
          width: '280px',
          background: 'var(--bg-secondary)',
          borderRight: '1px solid var(--border-color)',
          padding: '40px 24px',
          position: 'sticky',
          top: '73px',
          height: 'calc(100vh - 73px)',
          overflowY: 'auto',
        }}>
          <div style={{ marginBottom: '32px' }}>
            <h3 style={{
              fontSize: '12px',
              textTransform: 'uppercase',
              letterSpacing: '1px',
              color: 'var(--text-dim)',
              marginBottom: '16px',
            }}>
              Getting Started
            </h3>
            <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              {navItems.slice(0, 2).map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    padding: '10px 14px',
                    borderRadius: '8px',
                    color: pathname === item.href ? 'var(--accent-cyan)' : 'var(--text-secondary)',
                    background: pathname === item.href ? 'var(--accent-cyan-dim)' : 'transparent',
                    fontSize: '14px',
                    fontWeight: pathname === item.href ? 500 : 400,
                    transition: 'all 0.2s ease',
                    textDecoration: 'none',
                  }}
                >
                  {item.icon}
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>

          <div style={{ marginBottom: '32px' }}>
            <h3 style={{
              fontSize: '12px',
              textTransform: 'uppercase',
              letterSpacing: '1px',
              color: 'var(--text-dim)',
              marginBottom: '16px',
            }}>
              Reference
            </h3>
            <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              {navItems.slice(2).map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    padding: '10px 14px',
                    borderRadius: '8px',
                    color: pathname === item.href ? 'var(--accent-cyan)' : 'var(--text-secondary)',
                    background: pathname === item.href ? 'var(--accent-cyan-dim)' : 'transparent',
                    fontSize: '14px',
                    fontWeight: pathname === item.href ? 500 : 400,
                    transition: 'all 0.2s ease',
                    textDecoration: 'none',
                  }}
                >
                  {item.icon}
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>
        </aside>

        {/* Main Content */}
        <main style={{
          flex: 1,
          padding: '60px 80px',
          maxWidth: '900px',
        }}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            {children}
          </motion.div>
        </main>
      </div>
    </div>
  )
}