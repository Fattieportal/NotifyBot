'use client'

import { useState } from 'react'
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

export default function PlatformConfigurator() {
  const [selectedPlatform, setSelectedPlatform] = useState<string>('marktplaats')
  const [formData, setFormData] = useState<Record<string, any>>({})
  const [testResults, setTestResults] = useState<any>(null)
  const queryClient = useQueryClient()

  // Fetch platform schemas
  const { data: schemas } = useQuery({
    queryKey: ['platforms'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/api/platforms`)
      console.log('API Response:', res.data)
      console.log('Platforms:', res.data.platforms)
      return res.data.platforms as Record<string, PlatformSchema>
    },
  })

  // Test scrape mutation
  const testMutation = useMutation({
    mutationFn: async (data: any) => {
      const res = await axios.post(`${API_URL}/api/scrape/test`, {
        platform: selectedPlatform,
        config: data,
      })
      return res.data
    },
    onSuccess: (data) => {
      setTestResults(data)
    },
  })

  // Save configuration mutation
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
      alert('Configuration saved successfully!')
    },
  })

  const currentSchema = schemas?.[selectedPlatform]
  
  console.log('Current schemas:', schemas)
  console.log('Selected platform:', selectedPlatform)
  console.log('Current schema:', currentSchema)
  console.log('Current schema fields:', currentSchema?.fields)

  const handleFieldChange = (fieldName: string, value: any) => {
    setFormData((prev) => ({ ...prev, [fieldName]: value }))
  }

  const handleTestScrape = () => {
    testMutation.mutate(formData)
  }

  const handleSave = () => {
    saveMutation.mutate(formData)
  }

  if (!schemas) {
    return <div className="text-center py-8">Loading platforms...</div>
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* Platform Selector */}
      <div className="lg:col-span-1">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Select Platform</h3>
          <div className="space-y-2">
            {Object.entries(schemas).map(([key, schema]) => (
              <button
                key={key}
                onClick={() => {
                  setSelectedPlatform(key)
                  setFormData({})
                  setTestResults(null)
                }}
                className={`
                  w-full text-left px-4 py-3 rounded-lg border-2 transition-all
                  ${selectedPlatform === key
                    ? 'border-primary-500 bg-primary-50 text-primary-700 font-semibold'
                    : 'border-gray-200 hover:border-gray-300 text-gray-700'
                  }
                `}
              >
                {schema.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Configuration Form */}
      <div className="lg:col-span-2">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">
            Configure {currentSchema?.name}
          </h3>

          <form className="space-y-6">
            {currentSchema?.fields.map((field) => (
              <div key={field.name}>
                <label className="label">
                  {field.label}
                  {field.required && <span className="text-red-500 ml-1">*</span>}
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
                    onChange={(e) => handleFieldChange(field.name, parseInt(e.target.value))}
                  />
                )}

                {field.type === 'select' && (
                  <select
                    className="input"
                    value={formData[field.name] || ''}
                    onChange={(e) => handleFieldChange(field.name, e.target.value)}
                  >
                    <option value="">Select {field.label}</option>
                    {field.options?.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                )}

                {field.type === 'checkbox' && (
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      className="h-4 w-4 text-primary-600 rounded border-gray-300 focus:ring-primary-500"
                      checked={formData[field.name] || false}
                      onChange={(e) => handleFieldChange(field.name, e.target.checked)}
                    />
                    <span className="ml-2 text-sm text-gray-600">{field.placeholder}</span>
                  </div>
                )}

                {field.type === 'multiselect' && (
                  <select
                    multiple
                    className="input"
                    value={formData[field.name] || []}
                    onChange={(e) => {
                      const selected = Array.from(e.target.selectedOptions, (option) => option.value)
                      handleFieldChange(field.name, selected)
                    }}
                  >
                    {field.options?.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                )}
              </div>
            ))}

            {/* Action Buttons */}
            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={handleTestScrape}
                disabled={testMutation.isPending}
                className="btn-secondary"
              >
                {testMutation.isPending ? '🔄 Testing...' : '🧪 Test Scrape'}
              </button>
              <button
                type="button"
                onClick={handleSave}
                disabled={saveMutation.isPending}
                className="btn-primary"
              >
                {saveMutation.isPending ? '💾 Saving...' : '💾 Save Configuration'}
              </button>
            </div>
          </form>

          {/* Test Results */}
          {testResults && (
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-3">Test Results</h4>
              
              {testResults.success ? (
                <div>
                  <p className="text-green-600 font-medium mb-2">
                    ✅ Found {testResults.listings?.length || 0} listings
                  </p>
                  {testResults.listings?.slice(0, 3).map((listing: any, i: number) => (
                    <div key={i} className="mb-2 p-3 bg-white rounded border border-gray-200">
                      <p className="font-medium text-sm">{listing.title}</p>
                      <p className="text-xs text-gray-600">{listing.price}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-red-600">❌ {testResults.error || 'Test failed'}</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
