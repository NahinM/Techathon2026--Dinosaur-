type DashboardFooterProps = {
  formattedClock: string
}

export function DashboardFooter({ formattedClock }: DashboardFooterProps) {
  return (
    <footer className="footer">
      <div>
        <span className="dot" />Simulator tick every 5s
      </div>
      <div className="mono">{formattedClock}</div>
    </footer>
  )
}