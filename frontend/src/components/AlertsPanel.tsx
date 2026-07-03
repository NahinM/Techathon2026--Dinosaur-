type AlertsPanelProps = {
    alerts: string[]
    clock: Date
}

export function AlertsPanel({ alerts, clock }: AlertsPanelProps) {
    return (
        <aside className="alerts-panel">
            <h2>Alerts</h2>
            {alerts.length > 0 ? (
                alerts.slice(0, 6).map((message, index) => (
                    <div className="alert-item" key={`${message}-${index}`}>
                        <div className="alert-bar" />
                        <div>
                            <div className="alert-text">{message}</div>
                            <div className="alert-time">{clock.toLocaleTimeString()}</div>
                        </div>
                    </div>
                ))
            ) : (
                <div className="no-alerts">No active alerts. Everything's behaving.</div>
            )}
        </aside>
    )
}