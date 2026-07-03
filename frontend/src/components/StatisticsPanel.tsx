type StatItem = {
    label: string
    value: number
    unit: string
}

type StatisticsPanelProps = {
    stats: StatItem[]
}

export function StatisticsPanel({ stats }: StatisticsPanelProps) {
    return (
        <section className="stats-section">
            <div className="section-label">Statistics</div>
            <div className="stats-grid">
                {stats.map((stat) => (
                    <article className="stat-card" key={stat.label}>
                        <div className="stat-label">{stat.label}</div>
                        <div className="stat-value">
                            <span className="mono">{stat.value}</span>
                            <span className="stat-unit">{stat.unit}</span>
                        </div>
                    </article>
                ))}
            </div>
        </section>
    )
}