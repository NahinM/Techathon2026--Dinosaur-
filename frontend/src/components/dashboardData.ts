export type DeviceType = 'light' | 'fan'

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