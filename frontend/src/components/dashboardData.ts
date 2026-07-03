export type DeviceType = 'light' | 'fan'

export type StatItem = {
  label: string
  value: number
  unit: string
}

export type BackendDevice = {
  id: number
  room_id: number
  device_type: DeviceType
  status: string | boolean
  power?: number
  power_draw?: number
  name?: string
  last_changed?: string
  continuous_on_since?: string | null
}

export type BackendStats = {
  total: number
  'Drawing Room': number
  'Work Room 1': number
  'Work Room 2': number
}

export type Device = {
  id: number
  room: string
  name: string
  type: DeviceType
  status: boolean
  powerDraw: number
  lastChanged: string
  continuousOnSince: string | null
}

export const ROOMS = ['Drawing Room', 'Work Room 1', 'Work Room 2']

export const POWER: Record<DeviceType, number> = {
  light: 12,
  fan: 55,
}

const ROOM_BY_ID: Record<number, string> = {
  1: 'Drawing Room',
  2: 'Work Room 1',
  3: 'Work Room 2',
}

const DEVICE_NAME_BY_ID: Record<number, string> = {
  1: 'Fan 1',
  2: 'Fan 2',
  3: 'Light 1',
  4: 'Light 2',
  5: 'Light 3',
  6: 'Fan 1',
  7: 'Fan 2',
  8: 'Light 1',
  9: 'Light 2',
  10: 'Light 3',
  11: 'Fan 1',
  12: 'Fan 2',
  13: 'Light 1',
  14: 'Light 2',
  15: 'Light 3',
}

export function createDefaultStats(): StatItem[] {
  return [
    { label: 'Total Power draw', value: 0, unit: 'W' },
    { label: 'Drawing Room', value: 0, unit: 'W' },
    { label: 'Work Room 1', value: 0, unit: 'W' },
    { label: 'Work Room 2', value: 0, unit: 'W' },
  ]
}

export function normalizeStatus(status: string | boolean): boolean {
  if (typeof status === 'boolean') {
    return status
  }

  return ['on', 'true', '1'].includes(status.trim().toLowerCase())
}

export function mapBackendDevices(devices: BackendDevice[], previousDevices: Device[] = []): Device[] {
  const previousById = new Map(previousDevices.map((device) => [device.id, device]))
  const now = new Date().toISOString()

  return devices.map((device) => {
    const existingDevice = previousById.get(device.id)
    const normalizedStatus = normalizeStatus(device.status)
    const room = ROOM_BY_ID[device.room_id] ?? `Room ${device.room_id}`
    const name = device.name ?? DEVICE_NAME_BY_ID[device.id] ?? `Device ${device.id}`
    const powerDraw = Number(device.power ?? device.power_draw ?? 0)
    const lastChanged = device.last_changed ?? now
    const continuousOnSince = device.continuous_on_since ?? (normalizedStatus ? now : null)

    return {
      id: device.id,
      room,
      name,
      type: device.device_type,
      status: normalizedStatus,
      powerDraw,
      lastChanged:
        existingDevice && existingDevice.status === normalizedStatus && existingDevice.powerDraw === powerDraw
          ? existingDevice.lastChanged
          : lastChanged,
      continuousOnSince:
        existingDevice && existingDevice.status === normalizedStatus
          ? existingDevice.continuousOnSince
          : normalizedStatus
            ? continuousOnSince
            : null,
    }
  })
}

export function mapStatsResponse(stats: BackendStats): StatItem[] {
  return [
    { label: 'Total Power draw', value: Number(stats.total ?? 0), unit: 'W' },
    { label: 'Drawing Room', value: Number(stats['Drawing Room'] ?? 0), unit: 'W' },
    { label: 'Work Room 1', value: Number(stats['Work Room 1'] ?? 0), unit: 'W' },
    { label: 'Work Room 2', value: Number(stats['Work Room 2'] ?? 0), unit: 'W' },
  ]
}

export function createDevice(id: number, room: string, name: string, type: DeviceType): Device {
  const status = Math.random() > 0.5

  return {
    id,
    room,
    name,
    type,
    status,
    powerDraw: status ? POWER[type] : 0,
    lastChanged: new Date().toISOString(),
    continuousOnSince: status
      ? new Date(Date.now() - Math.random() * 7_200_000).toISOString()
      : null,
  }
}

export function createInitialDevices() {
  const initialDevices: Device[] = []
  let id = 1

  ROOMS.forEach((room) => {
    for (let index = 1; index <= 3; index += 1) {
      initialDevices.push(createDevice(id, room, `Light ${index}`, 'light'))
      id += 1
    }

    for (let index = 1; index <= 2; index += 1) {
      initialDevices.push(createDevice(id, room, `Fan ${index}`, 'fan'))
      id += 1
    }
  })

  return initialDevices
}