'use client'

import { useState } from 'react'
import type { ReactNode } from 'react'
import { useMutation } from '@tanstack/react-query'
import axios from 'axios'
import { API_URL } from '@/lib/api'

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

interface ChannelProps {
  icon: string
  title: string
  description: string
  enabled: boolean
  onToggle: (v: boolean) => void
  children?: ReactNode
  onTest: () => void
  testPending: boolean
}

function Channel({ icon, title, description, enabled, onToggle, children, onTest, testPending }: ChannelProps) {
  return (
    <div className={`rounded-2xl border transition-all duration-200 ${enabled ? 'border-white/15 bg-white/5' : 'border-white/5 bg-white/[0.02]'}`}>
      <div className="flex items-center justify-between p-5">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{icon}</span>
          <div>
            <h4 className="font-semibold text-white text-sm">{title}</h4>
            <p className="text-xs text-white/40">{description}</p>
          </div>
        </div>
        {/* Toggle */}
        <label className="relative inline-flex items-center cursor-pointer flex-shrink-0">
          <input
            type="checkbox"
            checked={enabled}
            onChange={(e) => onToggle(e.target.checked)}
            className="sr-only peer"
          />
          <div className="w-11 h-6 bg-white/10 rounded-full peer peer-checked:bg-blue-600 transition-colors after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-5" />
        </label>
      </div>

      {enabled && children && (
        <div className="px-5 pb-5 space-y-3 border-t border-white/5 pt-4">
          {children}
          <button
            onClick={onTest}
            disabled={testPending}
            className="btn-secondary !text-xs !py-1.5 !px-3 mt-1"
          >
            {testPending ? (
              <span className="flex items-center gap-2">
                <span className="w-3 h-3 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                Versturen...
              </span>
            ) : '📤 Test versturen'}
          </button>
        </div>
      )}
    </div>
  )
}

export default function NotificationSettings() {
  const [config, setConfig] = useState<NotificationConfig>({
    telegram_enabled: false,
    discord_enabled: false,
    email_enabled: false,
  })
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saved' | 'error'>('idle')

  const saveMutation = useMutation({
    mutationFn: async (data: NotificationConfig) => {
      const res = await axios.post(`${API_URL}/api/notifications/config`, data)
      return res.data
    },
    onSuccess: () => {
      setSaveStatus('saved')
      setTimeout(() => setSaveStatus('idle'), 3000)
    },
    onError: () => setSaveStatus('error'),
  })

  const testMutation = useMutation({
    mutationFn: async (type: 'telegram' | 'discord' | 'email') => {
      const payload: Record<string, string> = { type }
      if (type === 'telegram') {
        payload.token = config.telegram_token || ''
        payload.chat_id = config.telegram_chat_id || ''
      } else if (type === 'discord') {
        payload.webhook_url = config.discord_webhook || ''
      }
      const res = await axios.post(`${API_URL}/api/notifications/test`, payload)
      return res.data
    },
  })

  const up = (patch: Partial<NotificationConfig>) => setConfig((c) => ({ ...c, ...patch }))

  return (
    <div className="max-w-2xl space-y-4">
      {/* Telegram */}
      <Channel
        icon="📱"
        title="Telegram"
        description="Direct berichten via Telegram bot"
        enabled={config.telegram_enabled}
        onToggle={(v) => up({ telegram_enabled: v })}
        onTest={() => testMutation.mutate('telegram')}
        testPending={testMutation.isPending}
      >
        <div>
          <label className="label">Bot Token</label>
          <input
            type="text"
            className="input"
            placeholder="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
            value={config.telegram_token || ''}
            onChange={(e) => up({ telegram_token: e.target.value })}
          />
        </div>
        <div>
          <label className="label">Chat ID</label>
          <input
            type="text"
            className="input"
            placeholder="123456789"
            value={config.telegram_chat_id || ''}
            onChange={(e) => up({ telegram_chat_id: e.target.value })}
          />
        </div>
      </Channel>

      {/* Discord */}
      <Channel
        icon="💬"
        title="Discord"
        description="Notificaties in Discord channel via webhook"
        enabled={config.discord_enabled}
        onToggle={(v) => up({ discord_enabled: v })}
        onTest={() => testMutation.mutate('discord')}
        testPending={testMutation.isPending}
      >
        <div>
          <label className="label">Webhook URL</label>
          <input
            type="text"
            className="input"
            placeholder="https://discord.com/api/webhooks/..."
            value={config.discord_webhook || ''}
            onChange={(e) => up({ discord_webhook: e.target.value })}
          />
        </div>
      </Channel>

      {/* Email */}
      <Channel
        icon="📧"
        title="Email"
        description="Advertenties per e-mail ontvangen"
        enabled={config.email_enabled}
        onToggle={(v) => up({ email_enabled: v })}
        onTest={() => testMutation.mutate('email')}
        testPending={testMutation.isPending}
      >
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">SMTP Server</label>
            <input
              type="text"
              className="input"
              placeholder="smtp.gmail.com"
              value={config.email_smtp_server || ''}
              onChange={(e) => up({ email_smtp_server: e.target.value })}
            />
          </div>
          <div>
            <label className="label">Poort</label>
            <input
              type="number"
              className="input"
              placeholder="587"
              value={config.email_smtp_port || ''}
              onChange={(e) => up({ email_smtp_port: parseInt(e.target.value) })}
            />
          </div>
        </div>
        <div>
          <label className="label">Gebruikersnaam</label>
          <input
            type="text"
            className="input"
            placeholder="jouw-email@gmail.com"
            value={config.email_username || ''}
            onChange={(e) => up({ email_username: e.target.value })}
          />
        </div>
        <div>
          <label className="label">Wachtwoord</label>
          <input
            type="password"
            className="input"
            placeholder="App-wachtwoord"
            value={config.email_password || ''}
            onChange={(e) => up({ email_password: e.target.value })}
          />
        </div>
        <div>
          <label className="label">Verstuur naar</label>
          <input
            type="email"
            className="input"
            placeholder="ontvanger@example.com"
            value={config.email_to || ''}
            onChange={(e) => up({ email_to: e.target.value })}
          />
        </div>
      </Channel>

      {/* Save */}
      <div className="flex items-center gap-4 pt-2">
        <button
          onClick={() => saveMutation.mutate(config)}
          disabled={saveMutation.isPending}
          className="btn-primary"
        >
          {saveMutation.isPending
            ? <span className="flex items-center gap-2"><span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" /> Opslaan...</span>
            : '💾 Instellingen opslaan'}
        </button>
        {saveStatus === 'saved' && <span className="text-emerald-400 text-sm">✅ Opgeslagen!</span>}
        {saveStatus === 'error' && <span className="text-red-400 text-sm">❌ Opslaan mislukt</span>}
      </div>
    </div>
  )
}
