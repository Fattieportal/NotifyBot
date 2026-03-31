# Auto Notify - Frontend

Next.js 14 web application voor auto-advertentie monitoring.

## Features

- 🎨 Modern UI met Tailwind CSS
- 📊 Real-time statistics dashboard
- 🔧 Dynamic platform configuration forms
- 📋 Live listings table met auto-refresh
- 🔔 Notification settings management
- 🧪 Live "Test Scrape" functionaliteit
- 📱 Fully responsive design

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS 3.4
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **HTTP Client**: Axios
- **Icons**: Emoji (lightweight, no icon library needed)

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx          # Main dashboard page
│   ├── layout.tsx        # Root layout with React Query Provider
│   └── globals.css       # Global styles + Tailwind
├── components/
│   ├── StatsOverview.tsx         # Statistics cards
│   ├── PlatformConfigurator.tsx  # Platform config forms
│   ├── RecentListings.tsx        # Listings table
│   └── NotificationSettings.tsx  # Notification setup
├── public/               # Static assets
├── tailwind.config.ts    # Tailwind configuration
├── next.config.js        # Next.js configuration
├── tsconfig.json         # TypeScript configuration
└── package.json          # Dependencies
```

## Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Development

The frontend connects to the FastAPI backend at `http://localhost:8000` (in development) or `/api` (in production via Vercel rewrites).

### API Endpoints Used

- `GET /api/platforms` - Get platform schemas
- `POST /api/scrape/test` - Test scrape
- `POST /api/config` - Save configuration
- `GET /api/listings` - Get recent listings
- `GET /api/stats` - Get statistics
- `POST /api/notifications/config` - Save notification settings
- `POST /api/notifications/test` - Test notifications

## Components

### Dashboard (page.tsx)

Main entry point with:
- Navigation bar
- Stats overview
- Tab navigation (Configure / Listings / Notifications)
- Footer

### StatsOverview

4 statistics cards:
- Total Listings
- New Today
- Active Platforms
- Last Scrape Time

Auto-refreshes every 30 seconds.

### PlatformConfigurator

- Platform selector sidebar
- Dynamic form generator (based on FastAPI schemas)
- Test Scrape button with results preview
- Save Configuration button

### RecentListings

- Listings table with images
- Platform badges (color-coded)
- Live links to original ads
- Auto-refresh every 30 seconds

### NotificationSettings

Three notification types:
1. **Telegram** - Bot token & chat ID
2. **Discord** - Webhook URL
3. **Email** - SMTP configuration

Each with:
- Toggle switch (enable/disable)
- Configuration fields
- Test button

## Styling

Custom utility classes (see `globals.css`):

```css
.btn-primary    /* Blue button */
.btn-secondary  /* Gray button */
.btn-success    /* Green button */
.btn-danger     /* Red button */
.card           /* White card container */
.input          /* Form input */
.label          /* Form label */
```

## Deployment

### Vercel (Recommended)

1. Push to GitHub
2. Import in Vercel
3. Set root directory to `web-app/frontend`
4. Deploy

### Manual

```bash
npm run build
npm start
```

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions

## License

Private project
