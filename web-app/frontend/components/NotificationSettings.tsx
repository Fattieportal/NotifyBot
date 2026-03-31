'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import axios from 'axios'

interface NotificationConfig {
  telegram_enabled: boolean
  telegram_token?: string
  telegram_chat_id?: string
  discord_enabled: boolean
  discord_webhook?: string
  email_enabled: boolean
  email_smtp_server?: string
  email_smtp_port?: number
  email_username?: string
  email_password?: string
  email_to?: string
}

export default function NotificationSettings() {
  const [config, setConfig] = useState<NotificationConfig>({
    telegram_enabled: false,
    discord_enabled: false,
    email_enabled: false,
  })

  const saveMutation = useMutation({
    mutationFn: async (data: NotificationConfig) => {
      const res = await axios.post('/api/notifications/config', data)
      return res.data
    },
    onSuccess: () => {
      alert('Notification settings saved successfully!')
    },
  })

  const testMutation = useMutation({
    mutationFn: async (type: 'telegram' | 'discord' | 'email') => {
      const res = await axios.post('/api/notifications/test', { type })
      return res.data
    },
    onSuccess: (data) => {
      if (data.success) {
        alert('Test notification sent successfully!')
      } else {
        alert(`Test failed: ${data.error}`)
      }
    },
  })

  const handleSave = () => {
    saveMutation.mutate(config)
  }

  const handleTest = (type: 'telegram' | 'discord' | 'email') => {
    testMutation.mutate(type)
  }

  return (
    <div className="max-w-4xl">
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">
          Notification Settings
        </h3>

        <div className="space-y-8">
          {/* Telegram */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <span className="text-2xl">📱</span>
                <div>
                  <h4 className="font-semibold text-gray-900">Telegram</h4>
                  <p className="text-xs text-gray-500">
                    Get instant notifications via Telegram bot
                  </p>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={config.telegram_enabled}
                  onChange={(e) =>
                    setConfig({ ...config, telegram_enabled: e.target.checked })
                  }
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>

            {config.telegram_enabled && (
              <div className="pl-11 space-y-3">
                <div>
                  <label className="label">Bot Token</label>
                  <input
                    type="text"
                    className="input"
                    placeholder="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
                    value={config.telegram_token || ''}
                    onChange={(e) =>
                      setConfig({ ...config, telegram_token: e.target.value })
                    }
                  />
                </div>
                <div>
                  <label className="label">Chat ID</label>
                  <input
                    type="text"
                    className="input"
                    placeholder="123456789"
                    value={config.telegram_chat_id || ''}
                    onChange={(e) =>
                      setConfig({ ...config, telegram_chat_id: e.target.value })
                    }
                  />
                </div>
                <button
                  onClick={() => handleTest('telegram')}
                  disabled={testMutation.isPending}
                  className="btn-secondary text-sm"
                >
                  Send Test Message
                </button>
              </div>
            )}
          </div>

          {/* Discord */}
          <div className="border-t border-gray-200 pt-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <span className="text-2xl">💬</span>
                <div>
                  <h4 className="font-semibold text-gray-900">Discord</h4>
                  <p className="text-xs text-gray-500">
                    Post notifications to Discord webhook
                  </p>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={config.discord_enabled}
                  onChange={(e) =>
                    setConfig({ ...config, discord_enabled: e.target.checked })
                  }
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>

            {config.discord_enabled && (
              <div className="pl-11 space-y-3">
                <div>
                  <label className="label">Webhook URL</label>
                  <input
                    type="text"
                    className="input"
                    placeholder="https://discord.com/api/webhooks/..."
                    value={config.discord_webhook || ''}
                    onChange={(e) =>
                      setConfig({ ...config, discord_webhook: e.target.value })
                    }
                  />
                </div>
                <button
                  onClick={() => handleTest('discord')}
                  disabled={testMutation.isPending}
                  className="btn-secondary text-sm"
                >
                  Send Test Message
                </button>
              </div>
            )}
          </div>

          {/* Email */}
          <div className="border-t border-gray-200 pt-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <span className="text-2xl">📧</span>
                <div>
                  <h4 className="font-semibold text-gray-900">Email</h4>
                  <p className="text-xs text-gray-500">
                    Receive email notifications with listing details
                  </p>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={config.email_enabled}
                  onChange={(e) =>
                    setConfig({ ...config, email_enabled: e.target.checked })
                  }
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>

            {config.email_enabled && (
              <div className="pl-11 space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="label">SMTP Server</label>
                    <input
                      type="text"
                      className="input"
                      placeholder="smtp.gmail.com"
                      value={config.email_smtp_server || ''}
                      onChange={(e) =>
                        setConfig({ ...config, email_smtp_server: e.target.value })
                      }
                    />
                  </div>
                  <div>
                    <label className="label">Port</label>
                    <input
                      type="number"
                      className="input"
                      placeholder="587"
                      value={config.email_smtp_port || ''}
                      onChange={(e) =>
                        setConfig({ ...config, email_smtp_port: parseInt(e.target.value) })
                      }
                    />
                  </div>
                </div>
                <div>
                  <label className="label">Username</label>
                  <input
                    type="text"
                    className="input"
                    placeholder="your-email@gmail.com"
                    value={config.email_username || ''}
                    onChange={(e) =>
                      setConfig({ ...config, email_username: e.target.value })
                    }
                  />
                </div>
                <div>
                  <label className="label">Password</label>
                  <input
                    type="password"
                    className="input"
                    placeholder="App password"
                    value={config.email_password || ''}
                    onChange={(e) =>
                      setConfig({ ...config, email_password: e.target.value })
                    }
                  />
                </div>
                <div>
                  <label className="label">Send To</label>
                  <input
                    type="email"
                    className="input"
                    placeholder="recipient@example.com"
                    value={config.email_to || ''}
                    onChange={(e) =>
                      setConfig({ ...config, email_to: e.target.value })
                    }
                  />
                </div>
                <button
                  onClick={() => handleTest('email')}
                  disabled={testMutation.isPending}
                  className="btn-secondary text-sm"
                >
                  Send Test Email
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Save Button */}
        <div className="mt-8 pt-6 border-t border-gray-200">
          <button
            onClick={handleSave}
            disabled={saveMutation.isPending}
            className="btn-primary"
          >
            {saveMutation.isPending ? '💾 Saving...' : '💾 Save All Settings'}
          </button>
        </div>
      </div>
    </div>
  )
}
