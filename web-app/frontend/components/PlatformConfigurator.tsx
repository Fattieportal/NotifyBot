'use client'

import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { API_URL } from '@/lib/api'

interface PlatformSchema {
  name: string
  fields: {
    name: string
    label: string
    type: string
    required: boolean
    options?: string[]
    placeholder?: string
    default?: any
    min?: number
    max?: number
  }[]
}

const platformIcons: Record<string, string> = {
  marktplaats: '🟠',
  autoscout24: '🔵',
  facebook: '🟣',
  mobile_de: '🟢',
  ebay_kleinanzeigen: '🟡',
}

export default function PlatformConfigurator() {
  const [selectedPlatform, setSelectedPlatform] = useState<string>('marktplaats')
  const [formData, setFormData] = useState<Record<string, any>>({})
  const [testResults, setTestResults] = useState<any>(null)
  const queryClient = useQueryClient()

  const { data: schemas } = useQuery({
    queryKey: ['platforms'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/api/platforms`)
      let platformData = res.data.platforms || res.data
      if (Array.isArray(platformData)) {
        const obj: Record<string, PlatformSchema> = {}
        platformData.forEach((platform: any, index: number) => {
          const key = platform.id || platform.name?.toLowerCase().replace(/\s+/g, '_').replace(/\./g, '') || `platform_${index}`
          obj[key] = platform
        })
        platformData = obj
      }
      return platformData as Record<string, PlatformSchema>
    },
  })

  useEffect(() => {
    const saved = (schemas?.[selectedPlatform] as any)?.config
    if (saved && Object.keys(saved).length > 0) {
      setFormData(saved)
    } else {
      setFormData({})
    }
    setTestResults(null)
  }, [selectedPlatform, schemas])

  const testMutation = useMutation({
    mutationFn: async (data: any) => {
      const res = await axios.post(`${API_URL}/api/scrape/test`, {
        platform: selectedPlatform,
        config: data,
      })
      return res.data
    },
    onSuccess: (data) => setTestResults(data),
  })

  const saveMutation = useMutation({
    mutationFn: async (data: any) => {
      const res = await axios.post(`${API_URL}/api/config`, {
        platform: selectedPlatform,
        config: data,
        enabled: true,
      })
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stats'] })
    },
  })

  const currentSchema = schemas?.[selectedPlatform]

  const handleFieldChange = (fieldName: string, value: any) => {
    setFormData((prev) => ({ ...prev, [fieldName]: value }))
  }

  if (!schemas || typeof schemas !== 'object') {
    return (
      <div className="card flex items-center justify-center py-16">
        <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mr-3" />
        <span className="text-white/50">Platforms laden...</span>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Platform Selector */}
      <div className="lg:col-span-1">
        <div className="card !p-3">
          <p className="text-xs font-medium text-white/30 uppercase tracking-wider px-2 mb-3">Platforms</p>
          <div className="space-y-1">
            {Object.entries(schemas).map(([key, schema]) => (
              <button
                key={key}
                onClick={() => setSelectedPlatform(key)}
                className={`w-full text-left px-3 py-3 rounded-xl transition-all flex items-center gap-3 ${
                  selectedPlatform === key
                    ? 'bg-blue-600/20 border border-blue-500/30 text-white'
                    : 'hover:bg-white/5 border border-transparent text-white/60 hover:text-white'
                }`}
              >
                <span className="text-lg">{platformIcons[key] ?? '🔘'}</span>
                <span className="font-medium text-sm">{schema.name}</span>
                {selectedPlatform === key && (
                  <span className="ml-auto w-1.5 h-1.5 bg-blue-400 rounded-full" />
                )}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Configuration Form */}
      <div className="lg:col-span-2 space-y-4">
        <div className="card">
          <h3 className="text-base font-semibold text-white mb-5 flex items-center gap-2">
            <span>{platformIcons[selectedPlatform] ?? '🔘'}</span>
            {currentSchema?.name} configuratie
          </h3>

          <form className="space-y-4">
            {currentSchema?.fields?.map((field) => (
              <div key={field.name}>
                <label className="label">
                  {field.label}
                  {field.required && <span className="text-red-400 ml-1">*</span>}
                </label>

                {field.type === 'text' && (
                  <input
                    type="text"
                    className="input"
                    placeholder={field.placeholder}
                    value={formData[field.name] || ''}
                    onChange={(e) => handleFieldChange(field.name, e.target.value)}
                  />
                )}

                {field.type === 'number' && (
                  <input
                    type="number"
                    className="input"
                    placeholder={field.placeholder}
                    min={field.min}
                    max={field.max}
                    value={formData[field.name] || ''}
                    onChange={(e) => handleFieldChange(field.name, e.target.value ? parseInt(e.target.value) : undefined)}
                  />
                )}

                {field.type === 'select' && (
                  <select
                    className="input"
                    value={formData[field.name] || ''}
                    onChange={(e) => handleFieldChange(field.name, e.target.value)}
                  >
                    <option value="">Kies {field.label}</option>
                    {field.options?.map((option) => (
                      <option key={option} value={option}>{option}</option>
                    ))}
                  </select>
                )}

                {field.type === 'checkbox' && (
                  <label className="flex items-center gap-3 cursor-pointer group">
                    <div className="relative">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={formData[field.name] || false}
                        onChange={(e) => handleFieldChange(field.name, e.target.checked)}
                      />
                      <div className="w-10 h-6 bg-white/10 rounded-full peer peer-checked:bg-blue-600 transition-colors after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-4" />
                    </div>
                    <span className="text-sm text-white/60 group-hover:text-white/80 transition-colors">{field.placeholder}</span>
                  </label>
                )}

                {field.type === 'multiselect' && (
                  <select
                    multiple
                    className="input min-h-[120px]"
                    value={formData[field.name] || []}
                    onChange={(e) => {
                      const selected = Array.from(e.target.selectedOptions, (option) => option.value)
                      handleFieldChange(field.name, selected)
                    }}
                  >
                    {field.options?.map((option) => (
                      <option key={option} value={option}>{option}</option>
                    ))}
                  </select>
                )}
              </div>
            ))}

            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={() => testMutation.mutate(formData)}
                disabled={testMutation.isPending}
                className="btn-secondary"
              >
                {testMutation.isPending
                  ? <span className="flex items-center gap-2"><span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" /> Testen...</span>
                  : '🧪 Test Scrape'}
              </button>
              <button
                type="button"
                onClick={() => saveMutation.mutate(formData)}
                disabled={saveMutation.isPending}
                className="btn-primary"
              >
                {saveMutation.isPending
                  ? <span className="flex items-center gap-2"><span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" /> Opslaan...</span>
                  : saveMutation.isSuccess ? '✅ Opgeslagen!' : '💾 Opslaan'}
              </button>
            </div>
          </form>
        </div>

        {/* Test Results */}
        {testResults && (
          <div className={`card border ${testResults.success ? 'border-emerald-500/20 bg-emerald-500/5' : 'border-red-500/20 bg-red-500/5'}`}>
            <h4 className="font-semibold text-white mb-3 text-sm">Test Resultaten</h4>
            {testResults.success ? (
              <div className="space-y-2">
                <p className="text-emerald-400 font-medium text-sm">
                  ✅ {testResults.listings?.length || 0} advertenties gevonden
                </p>
                {testResults.listings?.slice(0, 3).map((listing: any, i: number) => (
                  <div key={i} className="p-3 bg-white/5 rounded-xl border border-white/10">
                    <p className="font-medium text-sm text-white truncate">{listing.title}</p>
                    <p className="text-blue-400 text-xs font-bold mt-0.5">{listing.price}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-red-400 text-sm">❌ {testResults.error || 'Test mislukt'}</p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
