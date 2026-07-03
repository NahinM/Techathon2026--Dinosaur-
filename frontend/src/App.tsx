import { useEffect, useState } from 'react'
import './App.css'
import { AlertsPanel } from './components/AlertsPanel'
import { DashboardFooter } from './components/DashboardFooter'
import { DashboardHeader } from './components/DashboardHeader'
import { FloorplanSection } from './components/FloorplanSection'
import { StatisticsPanel } from './components/StatisticsPanel'
import {
  ROOMS,
  createDefaultStats,
  createInitialDevices,
  mapBackendDevices,
  mapStatsResponse,
  type BackendDevice,
  type Device,
  type StatItem,
} from './components/dashboardData'
import { io } from 'socket.io-client'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? 'http://127.0.0.1:5000'
const API_BASE_URL = BACKEND_URL.replace(/\/$/, '')

function App() {
  const [devices, setDevices] = useState<Device[]>([])
  const [stats, setStats] = useState<StatItem[]>(() => createDefaultStats())
  const [todayKwh, setTodayKwh] = useState(4.2)
  const [clock, setClock] = useState(() => new Date())
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'offline'>('connecting')
  const totalPower = devices.reduce((sum, device) => sum + device.powerDraw, 0)

  useEffect(() => {
    const clockInterval = window.setInterval(() => {
      setClock(new Date())
    }, 1000)

    const loadInitialState = async () => {
      try {
        const [devicesResponse, statsResponse] = await Promise.all([
          fetch(`${API_BASE_URL}/api/devices`),
          fetch(`${API_BASE_URL}/api/stats`),
        ])

        if (!devicesResponse.ok) {
          throw new Error(`Failed to load devices: ${devicesResponse.status}`)
        }

        if (!statsResponse.ok) {
          throw new Error(`Failed to load stats: ${statsResponse.status}`)
        }

        const devicesData = (await devicesResponse.json()) as BackendDevice[]
        const statsData = await statsResponse.json()

        setDevices(mapBackendDevices(devicesData))
        setStats(mapStatsResponse(statsData))
      } catch {
        setDevices(createInitialDevices())
        setConnectionStatus('offline')
      }
    }

    void loadInitialState()

    const socket = io(BACKEND_URL, {
      transports: ['websocket'],
    })

    socket.on('connect', () => {
      setConnectionStatus('connected')
    })

    socket.on('disconnect', () => {
      setConnectionStatus('offline')
    })

    socket.on('connect_error', () => {
      setConnectionStatus('offline')
    })

    socket.on('state_update', (payload: { devices?: BackendDevice[]; stats?: { total: number; 'Dining Room': number; 'Work Room 1': number; 'Work Room 2': number } }) => {
      if (payload.devices) {
        setDevices((currentDevices) => mapBackendDevices(payload.devices ?? [], currentDevices))
      }

      if (payload.stats) {
        setStats(mapStatsResponse(payload.stats))
      }
    })

    return () => {
      window.clearInterval(clockInterval)
      socket.disconnect()
    }
  }, [])

  useEffect(() => {
    const usageInterval = window.setInterval(() => {
      setTodayKwh((currentKwh) => currentKwh + (totalPower / 1000) * (5 / 3600))
    }, 5000)

    return () => {
      window.clearInterval(usageInterval)
    }
  }, [totalPower])

  const formattedClock = clock.toLocaleString()
  const alerts = buildAlerts(devices, clock)

  return (
    <div className="dashboard-shell">
      <div className="dashboard-backdrop dashboard-backdrop-a" />
      <div className="dashboard-backdrop dashboard-backdrop-b" />

      <main className="wrap">
        <DashboardHeader totalPower={totalPower} todayKwh={todayKwh} />

        <div className="connection-note">
          WebSocket status: <span>{connectionStatus}</span>
        </div>

        <StatisticsPanel stats={stats} />

        <FloorplanSection devices={devices} rooms={ROOMS} />

        <section className="body-grid">
          <AlertsPanel alerts={alerts} clock={clock} />
        </section>

        <DashboardFooter formattedClock={formattedClock} />
      </main>
    </div>
  )
}

function buildAlerts(devices: Device[], clock: Date) {
  const alerts: string[] = []
  const hour = clock.getHours()

  if (hour >= 17) {
    ROOMS.forEach((room) => {
      const stillOn = devices.filter((device) => device.room === room && device.status)

      if (stillOn.length > 0) {
        alerts.push(
          `${room} still has ${stillOn.length} device${stillOn.length > 1 ? 's' : ''} ON after 5 PM. Did someone forget to turn them off?`,
        )
      }
    })
  }

  devices
    .filter((device) => device.status && device.continuousOnSince)
    .forEach((device) => {
      const hoursOn = (Date.now() - new Date(device.continuousOnSince as string).getTime()) / 3_600_000

      if (hoursOn > 2) {
        alerts.push(`${device.name} in ${device.room} has been ON continuously for over 2 hours.`)
      }
    })

  return alerts
}

export default App
