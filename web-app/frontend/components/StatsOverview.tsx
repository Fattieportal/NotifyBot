'use client'

interface Stats {
  total_listings: number
  new_today: number
  platforms_active: number
  last_scrape?: string
}

interface StatsOverviewProps {
  stats?: Stats
  loading: boolean
}

const statCards = (stats?: Stats) => [
  {
    label: 'Totaal gevonden',
    value: stats?.total_listings ?? '—',
    icon: '📊',
    color: 'from-blue-500/20 to-blue-600/5',
    border: 'border-blue-500/20',
    text: 'text-blue-400',
  },
  {
    label: 'Vandaag nieuw',
    value: stats?.new_today ?? '—',
    icon: '✨',
    color: 'from-emerald-500/20 to-emerald-600/5',
    border: 'border-emerald-500/20',
    text: 'text-emerald-400',
  },
  {
    label: 'Actieve platforms',
    value: stats?.platforms_active ?? '—',
    icon: '🌐',
    color: 'from-purple-500/20 to-purple-600/5',
    border: 'border-purple-500/20',
    text: 'text-purple-400',
  },
  {
    label: 'Laatste scan',
    value: stats?.last_scrape
      ? new Date(stats.last_scrape).toLocaleTimeString('nl-NL', { hour: '2-digit', minute: '2-digit' })
      : '—',
    icon: '🕒',
    color: 'from-orange-500/20 to-orange-600/5',
    border: 'border-orange-500/20',
    text: 'text-orange-400',
  },
]

export default function StatsOverview({ stats, loading }: StatsOverviewProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="card animate-pulse h-28">
            <div className="h-3 bg-white/10 rounded w-1/2 mb-4" />
            <div className="h-8 bg-white/10 rounded w-1/3" />
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {statCards(stats).map((card, i) => (
        <div
          key={i}
          className={`relative overflow-hidden rounded-2xl border ${card.border} bg-gradient-to-br ${card.color} p-5`}
        >
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs text-white/40 font-medium uppercase tracking-wider">{card.label}</p>
              <p className={`mt-2 text-3xl font-bold ${card.text}`}>{card.value}</p>
            </div>
            <span className="text-2xl opacity-80">{card.icon}</span>
          </div>
        </div>
      ))}
    </div>
  )
}
