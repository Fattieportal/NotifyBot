'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { API_URL } from '@/lib/api'
import StatsOverview from '@/components/StatsOverview'
import PlatformConfigurator from '@/components/PlatformConfigurator'
import RecentListings from '@/components/RecentListings'
import NotificationSettings from '@/components/NotificationSettings'

const tabs = [
  { id: 'configure', label: 'Platforms', icon: '⚙️' },
  { id: 'listings',  label: 'Advertenties', icon: '🚗' },
  { id: 'notifications', label: 'Notificaties', icon: '🔔' },
] as const

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<'configure' | 'listings' | 'notifications'>('configure')

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['stats'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/api/stats`)
      return res.data
    },
    refetchInterval: 30000,
  })

  return (
    <div className="min-h-screen bg-[#0f1117]">
      {/* Gradient blobs */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl" />
        <div className="absolute top-1/2 -left-40 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl" />
      </div>

      {/* Navbar */}
      <nav className="sticky top-0 z-50 border-b border-white/5 bg-[#0f1117]/80 backdrop-blur-xl">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center text-lg shadow-lg shadow-blue-500/30">
                🚗
              </div>
              <div>
                <h1 className="text-base font-bold text-white leading-none">AutoNotify</h1>
                <p className="text-xs text-white/40 mt-0.5">Auto advertentie monitor</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {stats && (
                <span className="text-xs text-white/40">
                  {stats.platforms_active} platforms actief
                </span>
              )}
              <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
                <div className="h-1.5 w-1.5 bg-emerald-400 rounded-full animate-pulse" />
                <span className="text-xs text-emerald-400 font-medium">Live</span>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <main className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats */}
        <StatsOverview stats={stats} loading={statsLoading} />

        {/* Tabs */}
        <div className="mt-8">
          <div className="flex items-center gap-1 p-1 bg-white/5 rounded-2xl border border-white/5 w-fit">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={activeTab === tab.id ? 'tab-active' : 'tab-inactive'}
              >
                <span className="mr-1.5">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>

          <div className="mt-6">
            {activeTab === 'configure' && <PlatformConfigurator />}
            {activeTab === 'listings' && <RecentListings />}
            {activeTab === 'notifications' && <NotificationSettings />}
          </div>
        </div>
      </main>

      <footer className="relative mt-16 border-t border-white/5">
        <div className="mx-auto max-w-7xl px-4 py-6">
          <p className="text-center text-xs text-white/20">
            AutoNotify © 2026 — {stats?.platforms_active || 0} platforms gemonitord
          </p>
        </div>
      </footer>
    </div>
  )
}
