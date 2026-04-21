import { NextResponse } from 'next/server'
import { spawn } from 'child_process'
import path from 'path'
import os from 'os'
import type { LifeOSData } from '@/lib/types'

export const dynamic = 'force-dynamic'

export async function GET(): Promise<Response> {
  return new Promise((resolve) => {
    const homeDir = os.homedir()
    const dbPath = path.join(homeDir, '.lifeos', 'lifeos.db')

    // Check if database exists
    const fs = require('fs')
    if (!fs.existsSync(dbPath)) {
      resolve(NextResponse.json<LifeOSData>({
        projects: [],
        tasks: [],
        timeline: [],
        mood: [],
        stats: {
          totalTasks: 0,
          pendingTasks: 0,
          completedTasks: 0,
          currentStreak: 0,
          avgMood7Days: 0,
          activeProjects: 0
        }
      }))
      return
    }

    const scriptPath = path.join(process.cwd(), '..', 'lifeos', 'graph_export.py')

    const proc = spawn('python3', [scriptPath], {
      cwd: path.join(process.cwd(), '..'),
      env: { ...process.env, PYTHONPATH: path.join(process.cwd(), '..') }
    })

    let stdout = ''
    let stderr = ''

    proc.stdout.on('data', (data) => {
      stdout += data.toString()
    })

    proc.stderr.on('data', (data) => {
      stderr += data.toString()
    })

    proc.on('close', (code) => {
      if (code === 0) {
        try {
          const data = JSON.parse(stdout) as LifeOSData
          resolve(NextResponse.json<LifeOSData>(data))
        } catch {
          resolve(NextResponse.json<LifeOSData>({
            projects: [],
            tasks: [],
            timeline: [],
            mood: [],
            stats: {
              totalTasks: 0,
              pendingTasks: 0,
              completedTasks: 0,
              currentStreak: 0,
              avgMood7Days: 0,
              activeProjects: 0
            }
          }))
        }
      } else {
        console.error('Python script error:', stderr)
        resolve(NextResponse.json<LifeOSData>({
          projects: [],
          tasks: [],
          timeline: [],
          mood: [],
          stats: {
            totalTasks: 0,
            pendingTasks: 0,
            completedTasks: 0,
            currentStreak: 0,
            avgMood7Days: 0,
            activeProjects: 0
          }
        }))
      }
    })
  })
}