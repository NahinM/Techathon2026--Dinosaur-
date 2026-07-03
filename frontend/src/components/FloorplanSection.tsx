import type { Device } from './dashboardData'

type FloorplanSectionProps = {
  devices: Device[]
  rooms: string[]
}

export function FloorplanSection({ devices, rooms }: FloorplanSectionProps) {
  return (
    <section className="floorplan-section">
      <div className="section-label">Top-view office map · live</div>
      <div className="floorplan">
        {rooms.map((room) => {
          const roomDevices = devices.filter((device) => device.room === room)
          const roomPower = roomDevices.reduce((sum, device) => sum + device.powerDraw, 0)

          return (
            <article className="room" key={room}>
              <div className="room-name">{room}</div>
              <div className="room-power">
                Room load: <span className="num">{roomPower}</span> W
              </div>
              <div className="nodes">
                {roomDevices.map((device) => (
                  <div className={`node ${device.type === 'fan' ? 'fan-node' : ''}`} key={device.id}>
                    {device.type === 'light' ? (
                      <>
                        <div className={`bulb ${device.status ? 'on' : ''}`} />
                        <div className={device.status ? 'node-on-label' : 'node-off-label'}>{device.name}</div>
                      </>
                    ) : (
                      <>
                        <div className={`fan ${device.status ? 'on' : ''}`}>
                          <div className="blade-set">
                            <div className="blade" />
                            <div className="blade" />
                            <div className="blade" />
                            <div className="blade" />
                            <div className="hub" />
                          </div>
                        </div>
                        <div className={device.status ? 'node-on-label' : 'node-off-label'}>{device.name}</div>
                      </>
                    )}
                  </div>
                ))}
              </div>
            </article>
          )
        })}
      </div>
    </section>
  )
}