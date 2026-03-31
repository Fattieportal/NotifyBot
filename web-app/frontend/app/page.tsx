'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import StatsOverview from '@/components/StatsOverview'
import PlatformConfigurator from '@/components/PlatformConfigurator'
import RecentListings from '@/components/RecentListings'
import NotificationSettings from '@/components/NotificationSettings'

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<'configure' | 'listings' | 'notifications'>('configure')
  
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  // Fetch stats
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['stats'],
    queryFn: async () => {
      const res = await axios.get(`${apiUrl}/api/stats`)
      return res.data
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center gap-3">
              <span className="text-3xl">🚗</span>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Auto Notify</h1>
                <p className="text-xs text-gray-500">Multi-Platform Car Notifications</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">
                {stats ? `${stats.platforms_active} platforms active` : 'Loading...'}
              </span>
              <div className="h-2 w-2 bg-green-500 rounded-full"></div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Overview */}
        <StatsOverview stats={stats} loading={statsLoading} />

        {/* Tabs */}
        <div className="mt-8">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('configure')}
                className={`
                  whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm
                  ${activeTab === 'configure'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                🔧 Configure Platforms
              </button>
              <button
                onClick={() => setActiveTab('listings')}
                className={`
                  whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm
                  ${activeTab === 'listings'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                📋 Recent Listings
              </button>
              <button
                onClick={() => setActiveTab('notifications')}
                className={`
                  whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm
                  ${activeTab === 'notifications'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                🔔 Notifications
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          <div className="mt-8">
            {activeTab === 'configure' && <PlatformConfigurator />}
            {activeTab === 'listings' && <RecentListings />}
            {activeTab === 'notifications' && <NotificationSettings />}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-16 border-t border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-500">
            Auto Notify Web App © 2026 - Monitoring {stats?.platforms_active || 0} platforms
          </p>
        </div>
      </footer>
    </div>
  )
}
