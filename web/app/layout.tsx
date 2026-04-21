import type { Metadata } from 'next'
import './globals.css'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'LifeOS - Your Second Brain, In The Terminal',
  description: 'A privacy-first, local-first CLI productivity tool that turns unstructured thoughts into organized tasks, projects, and insights — powered by a local LLM.',
  icons: {
    icon: '/favicon.jpeg',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="noise-overlay" />
        {children}
      </body>
    </html>
  )
}