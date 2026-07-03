type DashboardHeaderProps = {
  totalPower: number
  todayKwh: number
}

export function DashboardHeader({ totalPower, todayKwh }: DashboardHeaderProps) {
  return (
    <header className="header">
      <div>
        <div className="brand-eyebrow">Small Office · Live Monitoring</div>
        <h1>Office Power Monitor</h1>
        <div className="subline">Drawing Room &nbsp;·&nbsp; Work Room 1 &nbsp;·&nbsp; Work Room 2</div>
      </div>

      <div className="readouts">
        <div className="readout">
          <div className="label">Current Total Power</div>
          <div className="value power">
            <span className="mono">{totalPower}</span>
            <span className="unit">W</span>
          </div>
        </div>
        <div className="readout">
          <div className="label">Today's Est. Usage</div>
          <div className="value">
            <span className="mono">{todayKwh.toFixed(1)}</span>
            <span className="unit">kWh</span>
          </div>
        </div>
      </div>
    </header>
  )
}