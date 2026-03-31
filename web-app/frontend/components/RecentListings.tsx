'use client'

import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { API_URL } from '@/lib/api'

interface Listing {
  id: string
  platform: string
  title: string
  price: string
  location: string
  url: string
  image_url?: string
  created_at: string
}

export default function RecentListings() {
  const { data: listings, isLoading } = useQuery({
    queryKey: ['listings'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/api/listings?limit=50`)
      return res.data as Listing[]
    },
    refetchInterval: 30000,
  })

  if (isLoading) {
    return (
      <div className="card">
        <div className="animate-pulse space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-24 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    )
  }

  if (!listings || listings.length === 0) {
    return (
      <div className="card text-center py-12">
        <p className="text-gray-500 text-lg">📭 No listings found yet</p>
        <p className="text-sm text-gray-400 mt-2">
          Configure platforms and wait for new listings to appear
        </p>
      </div>
    )
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">
        Recent Listings ({listings.length})
      </h3>

      <div className="space-y-4">
        {listings.map((listing) => (
          <div
            key={listing.id}
            className="flex gap-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
          >
            {/* Image */}
            {listing.image_url && (
              <div className="flex-shrink-0">
                <img
                  src={listing.image_url}
                  alt={listing.title}
                  className="w-24 h-24 object-cover rounded-lg"
                  onError={(e) => {
                    e.currentTarget.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"%3E%3Crect fill="%23ddd" width="100" height="100"/%3E%3Ctext x="50" y="50" text-anchor="middle" dy=".3em" fill="%23999" font-size="40"%3E🚗%3C/text%3E%3C/svg%3E'
                  }}
                />
              </div>
            )}

            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="text-base font-semibold text-gray-900 truncate">
                    {listing.title}
                  </h4>
                  <p className="text-sm text-gray-600 mt-1">
                    📍 {listing.location}
                  </p>
                </div>
                <span className={`
                  px-3 py-1 rounded-full text-xs font-medium ml-4
                  ${listing.platform === 'marktplaats' && 'bg-orange-100 text-orange-700'}
                  ${listing.platform === 'autoscout24' && 'bg-blue-100 text-blue-700'}
                  ${listing.platform === 'mobile_de' && 'bg-green-100 text-green-700'}
                  ${listing.platform === 'facebook' && 'bg-indigo-100 text-indigo-700'}
                  ${listing.platform === 'ebay_kleinanzeigen' && 'bg-yellow-100 text-yellow-700'}
                `}>
                  {listing.platform}
                </span>
              </div>

              <div className="flex items-center justify-between mt-3">
                <span className="text-lg font-bold text-primary-600">
                  {listing.price}
                </span>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-gray-500">
                    {new Date(listing.created_at).toLocaleString()}
                  </span>
                  <a
                    href={listing.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-primary text-sm py-1 px-3"
                  >
                    View →
                  </a>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
