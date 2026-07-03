import { useEffect, useState } from 'react'
import './App.css'
import { AlertsPanel } from './components/AlertsPanel'
import { DashboardFooter } from './components/DashboardFooter'
import { DashboardHeader } from './components/DashboardHeader'
import { FloorplanSection } from './components/FloorplanSection'
import { StatisticsPanel } from './components/StatisticsPanel'
import { POWER, ROOMS, createInitialDevices, type Device } from './components/dashboardData'

function App() {
  const [devices, setDevices] = useState<Device[]>(() => createInitialDevices())
  const [todayKwh, setTodayKwh] = useState(4.2)
  const [clock, setClock] = useState(() => new Date())

  useEffect(() => {
    const clockInterval = window.setInterval(() => {
      setClock(new Date())
    }, 1000)

    const simulationInterval = window.setInterval(() => {
      setDevices((currentDevices) => {
        const nextDevices = currentDevices.map((device) => ({ ...device }))
        const target = nextDevices[Math.floor(Math.random() * nextDevices.length)]

        if (target) {
          target.status = !target.status
          target.powerDraw = target.status ? POWER[target.type] : 0
          target.lastChanged = new Date().toISOString()
          target.continuousOnSince = target.status ? new Date().toISOString() : null
        }

        setTodayKwh((currentKwh) => {
          const totalPower = nextDevices.reduce((sum, device) => sum + device.powerDraw, 0)
          return currentKwh + (totalPower / 1000) * (5 / 3600)
        })

        return nextDevices
      })
    }, 5000)

    return () => {
      window.clearInterval(clockInterval)
      window.clearInterval(simulationInterval)
    }
  }, [])

  const totalPower = devices.reduce((sum, device) => sum + device.powerDraw, 0)
  const statistics = buildStatistics(devices)

  const formattedClock = clock.toLocaleString()
  const alerts = buildAlerts(devices, clock)

  return (
    <div className="dashboard-shell">
      <div className="dashboard-backdrop dashboard-backdrop-a" />
      <div className="dashboard-backdrop dashboard-backdrop-b" />

      <main className="wrap">
        <DashboardHeader totalPower={totalPower} todayKwh={todayKwh} />

        <StatisticsPanel stats={statistics} />

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

function buildStatistics(devices: Device[]) {
  const roomTotals = ROOMS.reduce<Record<string, number>>((accumulator, room) => {
    accumulator[room] = devices
      .filter((device) => device.room === room)
      .reduce((sum, device) => sum + device.powerDraw, 0)
    return accumulator
  }, {})

  return [
    { label: 'Total Power draw', value: devices.reduce((sum, device) => sum + device.powerDraw, 0), unit: 'W' },
    { label: 'Dining Room', value: roomTotals['Drawing Room'] ?? 0, unit: 'W' },
    { label: 'Work Room 1', value: roomTotals['Work Room 1'] ?? 0, unit: 'W' },
    { label: 'Work Room 2', value: roomTotals['Work Room 2'] ?? 0, unit: 'W' },
  ]
}

export default App
