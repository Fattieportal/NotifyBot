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

export default function StatsOverview({ stats, loading }: StatsOverviewProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="card animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-3"></div>
            <div className="h-8 bg-gray-200 rounded w-3/4"></div>
          </div>
        ))}
      </div>
    )
  }

  const statCards = [
    {
      label: 'Total Listings',
      value: stats?.total_listings || 0,
      icon: '📊',
      color: 'text-blue-600',
    },
    {
      label: 'New Today',
      value: stats?.new_today || 0,
      icon: '🆕',
      color: 'text-green-600',
    },
    {
      label: 'Active Platforms',
      value: stats?.platforms_active || 0,
      icon: '🌐',
      color: 'text-purple-600',
    },
    {
      label: 'Last Scrape',
      value: stats?.last_scrape ? new Date(stats.last_scrape).toLocaleTimeString() : 'Never',
      icon: '🕒',
      color: 'text-orange-600',
    },
  ]

  return (
    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
      {statCards.map((card, index) => (
        <div key={index} className="card hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{card.label}</p>
              <p className={`mt-2 text-3xl font-semibold ${card.color}`}>
                {card.value}
              </p>
            </div>
            <span className="text-4xl">{card.icon}</span>
          </div>
        </div>
      ))}
    </div>
  )
}
