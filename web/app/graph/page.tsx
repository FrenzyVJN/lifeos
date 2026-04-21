'use client'

import { useEffect } from 'react'
import { useGraphStore } from '@/lib/store'
import GraphCanvas from '@/components/graph/GraphCanvas'
import GraphUI from '@/components/graph/GraphUI'
import Link from 'next/link'
import { Brain, ArrowLeft } from 'lucide-react'

export default function GraphPage() {
  const { fetchData } = useGraphStore()

  useEffect(() => {
    fetchData()
  }, [fetchData])

  return (
    <div style={{ width: '100vw', height: '100vh', background: '#0a0a0f', position: 'relative', overflow: 'hidden' }}>
      {/* Navigation */}
      <nav style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        padding: '16px 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        zIndex: 200,
        background: 'linear-gradient(180deg, rgba(10, 10, 15, 0.9) 0%, rgba(10, 10, 15, 0) 100%)'
      }}>
        <Link href="/" style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          textDecoration: 'none',
          color: '#f0f0f5',
          fontFamily: 'Syne, sans-serif',
          fontWeight: 700,
          fontSize: '18px'
        }}>
          <Brain size={24} style={{ color: '#00e5ff' }} />
          Life<span style={{ color: '#00e5ff' }}>OS</span>
          <span style={{ color: '#606070', fontWeight: 400, marginLeft: '8px' }}>/ Graph</span>
        </Link>
        <Link href="/" style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          color: '#9090a0',
          textDecoration: 'none',
          fontSize: '14px',
          fontFamily: 'IBM Plex Sans, sans-serif',
          transition: 'color 0.2s ease'
        }}>
          <ArrowLeft size={16} />
          Back to Home
        </Link>
      </nav>

      {/* 3D Canvas */}
      <GraphCanvas />

      {/* UI Overlay */}
      <GraphUI />
    </div>
  )
}