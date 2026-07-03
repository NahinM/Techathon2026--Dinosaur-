import type { Device } from './dashboardData'

type DeviceListsProps = {
  devices: Device[]
  rooms: string[]
}

export function DeviceLists({ devices, rooms }: DeviceListsProps) {
  return (
    <div>
      {rooms.map((room) => {
        const roomDevices = devices.filter((device) => device.room === room)

        return (
          <section className="room-block" key={room}>
            <h2>{room}</h2>
            {roomDevices.map((device) => {
              const pillClass = device.status ? (device.type === 'light' ? 'on-light' : 'on-fan') : ''

              return (
                <div className="device-card" key={device.id}>
                  <div className="left">
                    <div className={`device-icon ${device.type} ${device.status ? 'active' : ''}`} />
                    <div>
                      <div className="name">{device.name}</div>
                      <div className="meta">
                        ID {String(device.id).padStart(3, '0')} · {device.powerDraw}W
                      </div>
                    </div>
                  </div>
                  <div className={`status-pill ${pillClass}`}>{device.status ? 'ON' : 'OFF'}</div>
                </div>
              )
            })}
          </section>
        )
      })}
    </div>
  )
}