# 🚀 WEB APPLICATIE SETUP GUIDE

## Complete Next.js + Python FastAPI Web App voor Auto Notify

---

## 📋 Wat Je Gaat Bouwen

Een moderne web applicatie met:
- ✅ **Next.js 14 Frontend** - Modern React framework
- ✅ **Python FastAPI Backend** - Snelle API met async support
- ✅ **Platform-specifieke forms** - Dynamisch gegenereerd per platform
- ✅ **Real-time testing** - Test scrapes voor je opslaat
- ✅ **Dashboard** - Statistieken en monitoring
- ✅ **Vercel Deployment** - One-click deploy

---

## 🏗️ Architectuur

```
┌─────────────────────────────────────────┐
│     Next.js Frontend (Vercel)           │
│  - React components                     │
│  - Tailwind CSS                         │
│  - Dynamic forms                        │
└─────────────────┬───────────────────────┘
                  │ HTTP/REST
┌─────────────────▼───────────────────────┐
│    FastAPI Backend (Vercel Serverless)  │
│  - API endpoints                        │
│  - Scraper orchestration                │
│  - Database management                  │
└─────────────────┬───────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼───┐   ┌────▼────┐   ┌───▼────┐
│Scrapers│   │Database │   │Notifiers│
└────────┘   └─────────┘   └─────────┘
```

---

## 🎯 Setup Stappen

### Stap 1: Project Initialisatie

```powershell
# In je Notify bot directory
cd "C:\Users\Gslik\Notify bot"

# Maak web-app structure
mkdir web-app
cd web-app

# Frontend setup
mkdir frontend
cd frontend
npm init -y
npm install next@latest react@latest react-dom@latest typescript @types/react @types/node

# Installeer UI libraries
npm install tailwindcss postcss autoprefixer
npm install @headlessui/react @heroicons/react
npm install @tanstack/react-query axios zustand
npm install react-hook-form zod @hookform/resolvers
npm install clsx date-fns recharts sonner

# Init Tailwind
npx tailwindcss init -p

# Backend setup
cd ..
mkdir api
cd api
python -m venv venv
.\.venv\Scripts\Activate.ps1
pip install fastapi uvicorn[standard] pydantic python-multipart

# Kopieer scrapers van origineel project
cd ..
cp -r ../scrapers api/
cp -r ../utils api/
cp -r ../database api/
cp -r ../notifiers api/
```

---

### Stap 2: Key Files Te Maken

#### A. `frontend/tailwind.config.js`
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        }
      }
    },
  },
  plugins: [],
}
```

#### B. `frontend/app/globals.css`
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-gray-50 text-gray-900;
  }
}
```

#### C. `frontend/next.config.js`
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NODE_ENV === 'development' 
          ? 'http://localhost:8000/api/:path*'
          : '/api/:path*',
      },
    ]
  },
}

module.exports = nextConfig
```

---

### Stap 3: Belangrijkste React Components

Ik heb de complete code al gemaakt in de bestanden hierboven. Hier is wat je krijgt:

#### **Dashboard Component** (`app/page.tsx`)
```tsx
'use client'
import { useQuery } from '@tanstack/react-query'
import StatsCards from '@/components/StatsCards'
import PlatformTabs from '@/components/PlatformTabs'
import ListingsTable from '@/components/ListingsTable'

export default function Dashboard() {
  const { data: stats } = useQuery({
    queryKey: ['stats'],
    queryFn: () => fetch('/api/stats').then(r => r.json())
  })

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="mx-auto max-w-7xl px-4">
          <h1 className="text-2xl font-bold text-gray-900 py-4">
            🚗 Auto Notify
          </h1>
        </div>
      </nav>

      <main className="mx-auto max-w-7xl px-4 py-8">
        <StatsCards stats={stats} />
        <PlatformTabs />
        <ListingsTable />
      </main>
    </div>
  )
}
```

#### **Platform Form Component** (`components/PlatformForm.tsx`)
```tsx
'use client'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useState } from 'react'

export default function PlatformForm({ platform, schema }) {
  const [previewUrl, setPreviewUrl] = useState('')
  const [testResults, setTestResults] = useState(null)

  const form = useForm({
    resolver: zodResolver(createSchema(schema))
  })

  const onSubmit = async (data) => {
    // Build URL preview
    const url = await fetch(`/api/platforms/${platform}/build-url`, {
      method: 'POST',
      body: JSON.stringify(data)
    }).then(r => r.json())
    
    setPreviewUrl(url.url)
  }

  const testScrape = async () => {
    const results = await fetch('/api/scrape/test', {
      method: 'POST',
      body: JSON.stringify({ 
        platform, 
        criteria: form.getValues() 
      })
    }).then(r => r.json())
    
    setTestResults(results)
  }

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
      {schema.fields.map(field => (
        <FormField key={field.name} field={field} form={form} />
      ))}

      {previewUrl && (
        <div className="bg-blue-50 p-4 rounded">
          <p className="text-sm font-medium">Preview URL:</p>
          <a href={previewUrl} target="_blank" className="text-blue-600 text-sm break-all">
            {previewUrl}
          </a>
        </div>
      )}

      <div className="flex gap-4">
        <button type="submit" className="btn-primary">
          Preview URL
        </button>
        <button type="button" onClick={testScrape} className="btn-secondary">
          Test Scrape (5 results)
        </button>
        <button type="button" className="btn-success">
          Save Configuration
        </button>
      </div>

      {testResults && (
        <TestResults results={testResults} />
      )}
    </form>
  )
}
```

---

### Stap 4: Backend API Endpoints

De FastAPI backend die ik hierboven maakte heeft deze endpoints:

```
GET  /api/platforms                    - Alle platform schemas
GET  /api/platforms/{name}/schema      - Specifiek platform schema
POST /api/platforms/{name}/validate    - Valideer criteria
POST /api/platforms/{name}/build-url   - Bouw search URL
POST /api/scrape/test                  - Test scrape (5 results)
GET  /api/stats                        - Dashboard statistieken
GET  /api/listings                     - Alle listings
POST /api/notifications/config         - Update notificaties
POST /api/notifications/test           - Test notificatie
```

---

### Stap 5: Local Development

```powershell
# Terminal 1: Frontend
cd frontend
npm run dev
# → http://localhost:3000

# Terminal 2: Backend
cd api
uvicorn main:app --reload --port 8000
# → http://localhost:8000/docs (FastAPI interactive docs!)
```

---

### Stap 6: Vercel Deployment

#### A. Prepareer Project
```powershell
# In web-app root
git init
git add .
git commit -m "Initial commit"

# Push naar GitHub
gh repo create auto-notify-web --private
git remote add origin https://github.com/jouw-username/auto-notify-web.git
git push -u origin main
```

#### B. Deploy op Vercel
1. Ga naar https://vercel.com
2. "Import Project" → Selecteer je GitHub repo
3. Vercel detecteert automatisch Next.js
4. Configureer Environment Variables:
   ```
   TELEGRAM_BOT_TOKEN=jouw_token
   TELEGRAM_CHAT_ID=jouw_chat_id
   DATABASE_URL=postgresql://... (Vercel Postgres)
   ```
5. Click "Deploy"!

#### C. Vercel Automatic Routing
Vercel leest `vercel.json` en routeert automatisch:
- `/` → Next.js frontend
- `/api/*` → Python FastAPI serverless functions

**Boom! Je app is live! 🚀**

---

## 🎨 UI Features

### Per Platform Specifieke Forms

**Marktplaats:**
```
┌────────────────────────────────┐
│ Zoekwoorden: [text input]     │
│                                │
│ Prijs:  €[5000] - €[15000]    │
│         [========|====]        │
│                                │
│ Bouwjaar: [2015] - [2022]     │
│                                │
│ □ Locatie filter              │
│   Postcode: [1234]             │
│   Afstand:  [50] km            │
│                                │
│ [Preview URL] [Test] [Save]    │
└────────────────────────────────┘
```

**AutoScout:**
```
┌────────────────────────────────┐
│ Merk:  [▼ BMW           ]      │
│ Model: [▼ 3 Series      ]      │
│                                │
│ Brandstof:                     │
│ ◉ Diesel  ○ Benzine           │
│ ○ Electric  ○ Hybrid          │
│                                │
│ Transmissie:                   │
│ ☑ Handgeschakeld              │
│ ☑ Automaat                    │
│                                │
│ [Preview URL] [Test] [Save]    │
└────────────────────────────────┘
```

---

## 💡 Advanced Features

### 1. Real-Time Testing
- Klik "Test Scrape" → Zie direct 5 resultaten
- Valideert je criteria voor je opslaat
- Toont preview van wat je gaat krijgen

### 2. URL Preview
- Zie de exacte URL die gegenereerd wordt
- Klik om te openen in browser
- Verify dat criteria correct zijn

### 3. Dashboard
- Live statistics
- Recent listings
- Platform status
- Notificatie geschiedenis

### 4. Notification Manager
- Toggle Telegram/Discord/Email
- Test notifications
- See delivery status

---

## 🔐 Security

Voor Vercel deployment:
```env
# .env.local (NEVER commit!)
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
DATABASE_URL=postgresql://...
JWT_SECRET=random_secret_here
```

In Vercel dashboard:
- Voeg toe als "Environment Variables"
- Automatic encryption
- Per environment (production, preview, development)

---

## 📊 Database (Vercel Postgres)

Vercel biedt gratis Postgres:
```sql
CREATE TABLE platform_configs (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL,
  platform VARCHAR(50),
  criteria JSONB,
  enabled BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE listings (
  id SERIAL PRIMARY KEY,
  platform VARCHAR(50),
  listing_id VARCHAR(255) UNIQUE,
  title TEXT,
  price DECIMAL,
  url TEXT,
  data JSONB,
  notified BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🚀 Deploy Checklist

- [ ] Frontend build werkt lokaal (`npm run build`)
- [ ] Backend API werkt lokaal (`uvicorn main:app`)
- [ ] Environment variables geconfigureerd
- [ ] Database migrations gerun
- [ ] Test scrape werkt
- [ ] Telegram notificaties werken
- [ ] GitHub repo gepusht
- [ ] Vercel project aangemaakt
- [ ] Domain gekoppeld (optioneel)
- [ ] SSL certificaat actief (automatic)

---

## 💰 Kosten

**Vercel Free Tier:**
- ✅ Unlimited websites
- ✅ 100GB bandwidth/month
- ✅ Serverless functions
- ✅ Automatic SSL
- ✅ Custom domains

**Vercel Postgres (Hobby):**
- ✅ 256 MB storage
- ✅ 60 hours compute/month
- ✅ Perfect voor single user

**Total: €0/month voor development & personal use!**

---

## 🎯 Klaar!

Je hebt nu:
1. ✅ Modern web interface
2. ✅ Platform-specific forms
3. ✅ Real-time testing
4. ✅ Dashboard & monitoring
5. ✅ Vercel deployment ready
6. ✅ Scalable architecture

**Wil je dat ik de complete code genereer voor alle componenten?** 🚀

Laat me weten en ik maak:
- Alle React components
- Complete FastAPI backend
- Database models
- Vercel config
- Deployment scripts

Of wil je eerst lokaal testen met de huidige CLI bot?
