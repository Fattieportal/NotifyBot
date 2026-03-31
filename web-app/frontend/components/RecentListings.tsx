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

const platformBadge: Record<string, string> = {
  marktplaats: 'badge-green',
  autoscout24: 'badge-blue',
  facebook: 'badge-blue',
  mobile_de: 'badge-green',
  ebay_kleinanzeigen: 'badge-gray',
}

const platformLabel: Record<string, string> = {
  marktplaats: 'Marktplaats',
  autoscout24: 'AutoScout24',
  facebook: 'Facebook',
  mobile_de: 'Mobile.de',
  ebay_kleinanzeigen: 'eBay KA',
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
      <div className="space-y-3">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="card animate-pulse h-28" />
        ))}
      </div>
    )
  }

  if (!listings || listings.length === 0) {
    return (
      <div className="card flex flex-col items-center justify-center py-20 text-center">
        <span className="text-5xl mb-4">📭</span>
        <p className="text-white/60 text-lg font-medium">Nog geen advertenties gevonden</p>
        <p className="text-white/30 text-sm mt-1">Configureer platforms en wacht op resultaten</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium text-white/40 uppercase tracking-wider">
          {listings.length} advertenties
        </h3>
      </div>

      {listings.map((listing) => (
        <div
          key={listing.id}
          className="card hover:border-white/20 transition-all duration-200 group"
        >
          <div className="flex gap-4">
            {/* Image */}
            {listing.image_url ? (
              <div className="flex-shrink-0 w-20 h-20 rounded-xl overflow-hidden bg-white/5">
                <img
                  src={listing.image_url}
                  alt={listing.title}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    e.currentTarget.style.display = 'none'
                  }}
                />
              </div>
            ) : (
              <div className="flex-shrink-0 w-20 h-20 rounded-xl bg-white/5 flex items-center justify-center text-3xl">
                🚗
              </div>
            )}

            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-3">
                <h4 className="text-white font-semibold truncate leading-snug">{listing.title}</h4>
                <span className={`flex-shrink-0 ${platformBadge[listing.platform] ?? 'badge-gray'}`}>
                  {platformLabel[listing.platform] ?? listing.platform}
                </span>
              </div>

              <p className="text-white/40 text-xs mt-1">📍 {listing.location}</p>

              <div className="flex items-center justify-between mt-3">
                <span className="text-blue-400 font-bold text-lg">{listing.price}</span>
                <div className="flex items-center gap-3">
                  <span className="text-white/25 text-xs hidden sm:block">
                    {new Date(listing.created_at).toLocaleString('nl-NL', {
                      day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit'
                    })}
                  </span>
                  <a
                    href={listing.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-primary !py-1 !px-3 text-sm"
                  >
                    Bekijk →
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
