# 🎨 Auto Notify - UI Design Specification

## Visual Layout

### 1. Navigation Bar
```
┌────────────────────────────────────────────────────────────────┐
│ 🚗 Auto Notify                    5 platforms active  🟢        │
│    Multi-Platform Car Notifications                             │
└────────────────────────────────────────────────────────────────┘
```

**Design**:
- White background (`bg-white`)
- Shadow border (`shadow-sm border-b`)
- Logo: 🚗 emoji + "Auto Notify" title
- Right: Active platforms count + green status dot

---

### 2. Stats Overview Cards

```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ 📊           │ 🆕           │ 🌐           │ 🕒           │
│ Total        │ New Today    │ Active       │ Last Scrape  │
│ Listings     │              │ Platforms    │              │
│              │              │              │              │
│ 1,234        │ 42           │ 5            │ 10:30 AM     │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

**Features**:
- 4 cards in responsive grid (1 col mobile, 2 col tablet, 4 col desktop)
- Each card: White background, rounded, shadow
- Emoji icon (top right)
- Label (gray text)
- Value (large, colored number)
- Hover effect: Increased shadow

**Colors**:
- Total Listings: Blue (`text-blue-600`)
- New Today: Green (`text-green-600`)
- Active Platforms: Purple (`text-purple-600`)
- Last Scrape: Orange (`text-orange-600`)

---

### 3. Tab Navigation

```
┌─────────────────────────────────────────────────────────────┐
│ 🔧 Configure Platforms  │  📋 Recent Listings  │  🔔 Notifications │
│ ━━━━━━━━━━━━━━━━━━━━━━                                      │
└─────────────────────────────────────────────────────────────┘
```

**Design**:
- Horizontal tabs below stats
- Active tab: Blue underline + blue text
- Inactive tabs: Gray text + hover effect
- Border bottom on container

---

### 4. Configure Platforms Tab

#### Layout: 2-Column Grid

**Left Column (1/3 width)**: Platform Selector
```
┌─────────────────────────┐
│ Select Platform         │
├─────────────────────────┤
│ ┌─────────────────────┐ │
│ │ Marktplaats         │ │  ← Active (blue border + bg)
│ └─────────────────────┘ │
│ ┌─────────────────────┐ │
│ │ AutoScout24         │ │  ← Inactive (gray border)
│ └─────────────────────┘ │
│ ┌─────────────────────┐ │
│ │ Mobile.de           │ │
│ └─────────────────────┘ │
│ ┌─────────────────────┐ │
│ │ Facebook            │ │
│ └─────────────────────┘ │
│ ┌─────────────────────┐ │
│ │ eBay Kleinanzeigen  │ │
│ └─────────────────────┘ │
└─────────────────────────┘
```

**Right Column (2/3 width)**: Configuration Form
```
┌──────────────────────────────────────────────────────┐
│ Configure Marktplaats                                │
├──────────────────────────────────────────────────────┤
│                                                       │
│ Zoekterm *                                           │
│ ┌──────────────────────────────────────────────────┐ │
│ │ BMW 3 serie                                      │ │
│ └──────────────────────────────────────────────────┘ │
│                                                       │
│ Prijs Min                                            │
│ ┌──────────────────────────────────────────────────┐ │
│ │ 5000                                             │ │
│ └──────────────────────────────────────────────────┘ │
│                                                       │
│ Prijs Max                                            │
│ ┌──────────────────────────────────────────────────┐ │
│ │ 15000                                            │ │
│ └──────────────────────────────────────────────────┘ │
│                                                       │
│ Postcode                                             │
│ ┌──────────────────────────────────────────────────┐ │
│ │ 1000                                             │ │
│ └──────────────────────────────────────────────────┘ │
│                                                       │
│ Afstand                                              │
│ ┌──────────────────────────────────────────────────┐ │
│ │ 50 km                                         ▼ │ │
│ └──────────────────────────────────────────────────┘ │
│                                                       │
│ Brandstof                                            │
│ ┌──────────────────────────────────────────────────┐ │
│ │ Benzine                                       ▼ │ │
│ └──────────────────────────────────────────────────┘ │
│                                                       │
│ ┌──────────────┐  ┌────────────────────────────┐    │
│ │ 🧪 Test      │  │ 💾 Save Configuration       │    │
│ │    Scrape    │  │                             │    │
│ └──────────────┘  └────────────────────────────┘    │
│                                                       │
│ ┌─ Test Results ────────────────────────────────┐   │
│ │ ✅ Found 12 listings                          │   │
│ │                                                │   │
│ │ ┌───────────────────────────────────────────┐ │   │
│ │ │ BMW 3 Serie 320i                          │ │   │
│ │ │ €12,500                                   │ │   │
│ │ └───────────────────────────────────────────┘ │   │
│ │ ┌───────────────────────────────────────────┐ │   │
│ │ │ BMW 3 Serie 318d                          │ │   │
│ │ │ €9,999                                    │ │   │
│ │ └───────────────────────────────────────────┘ │   │
│ └───────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
```

**Form Fields** (Dynamic per platform):
- Text inputs: Rounded, gray border, focus:blue
- Number inputs: Same styling
- Select dropdowns: Chevron icon, native select
- Checkboxes: Blue when checked
- Multi-select: Native HTML multiple select

**Buttons**:
- Test Scrape: Gray button (secondary)
- Save Config: Blue button (primary)
- Loading state: Spinner + "Testing..." / "Saving..."

**Test Results**:
- Gray background box (`bg-gray-50`)
- Success: Green checkmark + count
- Error: Red X + error message
- Listing previews: White cards with title + price

---

### 5. Recent Listings Tab

```
┌────────────────────────────────────────────────────────────────┐
│ Recent Listings (48)                                           │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ ┌────┐  BMW 3 Serie 320i Executive     [marktplaats] €12,500││
│ │ │IMG │  📍 Amsterdam                    23:45:12   [View →] ││
│ │ └────┘                                                       ││
│ └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ ┌────┐  Audi A4 2.0 TDI Quattro        [autoscout24] €15,999││
│ │ │IMG │  📍 Utrecht                      22:30:05   [View →] ││
│ │ └────┘                                                       ││
│ └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ ┌────┐  Mercedes C-Klasse C220 CDI     [mobile_de]  €13,750││
│ │ │IMG │  📍 Rotterdam                    21:15:33   [View →] ││
│ │ └────┘                                                       ││
│ └─────────────────────────────────────────────────────────────┘│
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

**Listing Card**:
- Gray background (`bg-gray-50`)
- Hover: Darker gray (`bg-gray-100`)
- Rounded corners
- Padding: 1rem

**Image**:
- 96x96px (w-24 h-24)
- Rounded corners
- Object-fit: cover
- Fallback: 🚗 emoji in SVG

**Content Layout**:
```
[Image] [Title                    ] [Platform Badge] [Price   ]
        [Location                 ] [Timestamp    ] [View Btn]
```

**Platform Badge Colors**:
- Marktplaats: Orange (`bg-orange-100 text-orange-700`)
- AutoScout24: Blue (`bg-blue-100 text-blue-700`)
- Mobile.de: Green (`bg-green-100 text-green-700`)
- Facebook: Indigo (`bg-indigo-100 text-indigo-700`)
- eBay: Yellow (`bg-yellow-100 text-yellow-700`)

**Empty State**:
```
┌────────────────────────────────────────┐
│                                         │
│          📭                             │
│     No listings found yet               │
│                                         │
│ Configure platforms and wait for        │
│ new listings to appear                  │
│                                         │
└────────────────────────────────────────┘
```

---

### 6. Notifications Tab

```
┌────────────────────────────────────────────────────────────┐
│ Notification Settings                                       │
├────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐│
│ │ 📱 Telegram                              [ ON / OFF ]   ││
│ │    Get instant notifications via Telegram bot           ││
│ │                                                          ││
│ │    Bot Token                                            ││
│ │    ┌──────────────────────────────────────────────────┐ ││
│ │    │ 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz           │ ││
│ │    └──────────────────────────────────────────────────┘ ││
│ │                                                          ││
│ │    Chat ID                                              ││
│ │    ┌──────────────────────────────────────────────────┐ ││
│ │    │ 123456789                                        │ ││
│ │    └──────────────────────────────────────────────────┘ ││
│ │                                                          ││
│ │    [Send Test Message]                                  ││
│ └─────────────────────────────────────────────────────────┘│
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐│
│ │ 💬 Discord                               [ ON / OFF ]   ││
│ │    Post notifications to Discord webhook                ││
│ │                                                          ││
│ │    Webhook URL                                          ││
│ │    ┌──────────────────────────────────────────────────┐ ││
│ │    │ https://discord.com/api/webhooks/...            │ ││
│ │    └──────────────────────────────────────────────────┘ ││
│ │                                                          ││
│ │    [Send Test Message]                                  ││
│ └─────────────────────────────────────────────────────────┘│
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐│
│ │ 📧 Email                                 [ ON / OFF ]   ││
│ │    Receive email notifications with listing details     ││
│ │                                                          ││
│ │    SMTP Server                     Port                 ││
│ │    ┌─────────────────────────┐   ┌─────────────────┐  ││
│ │    │ smtp.gmail.com          │   │ 587             │  ││
│ │    └─────────────────────────┘   └─────────────────┘  ││
│ │                                                          ││
│ │    Username                                             ││
│ │    ┌──────────────────────────────────────────────────┐ ││
│ │    │ your-email@gmail.com                            │ ││
│ │    └──────────────────────────────────────────────────┘ ││
│ │                                                          ││
│ │    Password                                             ││
│ │    ┌──────────────────────────────────────────────────┐ ││
│ │    │ ••••••••••••••••                                 │ ││
│ │    └──────────────────────────────────────────────────┘ ││
│ │                                                          ││
│ │    Send To                                              ││
│ │    ┌──────────────────────────────────────────────────┐ ││
│ │    │ recipient@example.com                            │ ││
│ │    └──────────────────────────────────────────────────┘ ││
│ │                                                          ││
│ │    [Send Test Email]                                    ││
│ └─────────────────────────────────────────────────────────┘│
│                                                             │
│ ┌──────────────────────────────────────────┐              │
│ │ 💾 Save All Settings                     │              │
│ └──────────────────────────────────────────┘              │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

**Toggle Switch**:
- iOS-style toggle
- Off: Gray background
- On: Blue background
- Animated transition

**Expandable Sections**:
- Only show fields when toggle is ON
- Smooth expand/collapse animation

**Test Buttons**:
- Gray secondary style
- Per notification type
- Shows loading state during test

---

### 7. Footer

```
┌────────────────────────────────────────────────────────────┐
│ Auto Notify Web App © 2026 - Monitoring 5 platforms        │
└────────────────────────────────────────────────────────────┘
```

**Design**:
- White background
- Top border
- Centered text
- Gray text color
- Small text size

---

## Color Palette

### Primary Colors
```
Primary:   #2563eb (Blue 600)   - Main actions, links
Success:   #16a34a (Green 600)  - Success states
Warning:   #f59e0b (Amber 500)  - Warnings
Danger:    #dc2626 (Red 600)    - Errors, delete actions
```

### Neutral Colors
```
Gray 50:   #f9fafb  - Backgrounds
Gray 100:  #f3f4f6  - Hover states
Gray 200:  #e5e7eb  - Borders
Gray 500:  #6b7280  - Secondary text
Gray 600:  #4b5563  - Labels
Gray 900:  #111827  - Primary text
```

### Platform Colors
```
Marktplaats:   #ff6600 (Orange)
AutoScout24:   #2563eb (Blue)
Mobile.de:     #16a34a (Green)
Facebook:      #6366f1 (Indigo)
eBay:          #fbbf24 (Yellow)
```

---

## Typography

### Font Family
```css
font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
```

### Font Sizes
```
Heading 1: text-xl (20px) - Page titles
Heading 2: text-lg (18px) - Section titles
Heading 3: text-base (16px) - Card titles
Body:      text-sm (14px) - Normal text
Small:     text-xs (12px) - Labels, timestamps
```

### Font Weights
```
font-normal:   400 - Body text
font-medium:   500 - Labels
font-semibold: 600 - Titles
font-bold:     700 - Numbers, emphasis
```

---

## Spacing

### Component Spacing
```
Card padding:    p-6 (1.5rem)
Card gap:        gap-5 (1.25rem)
Form spacing:    space-y-6 (1.5rem)
Button padding:  px-4 py-2 (1rem x 0.5rem)
Input padding:   px-3 py-2 (0.75rem x 0.5rem)
```

### Layout Spacing
```
Max width:  max-w-7xl (1280px)
Padding X:  px-4 sm:px-6 lg:px-8
Padding Y:  py-8 (2rem)
```

---

## Interactive States

### Buttons
```css
/* Default */
background: #2563eb;
color: white;

/* Hover */
background: #1d4ed8;

/* Focus */
ring: 2px solid #93c5fd;

/* Disabled */
background: #9ca3af;
cursor: not-allowed;
```

### Inputs
```css
/* Default */
border: 1px solid #d1d5db;

/* Focus */
border: 1px solid #2563eb;
ring: 2px solid #93c5fd;

/* Error */
border: 1px solid #dc2626;
```

### Cards
```css
/* Default */
box-shadow: 0 1px 3px rgba(0,0,0,0.1);

/* Hover */
box-shadow: 0 4px 6px rgba(0,0,0,0.1);
transition: all 0.2s;
```

---

## Responsive Breakpoints

```css
/* Mobile First */
sm: 640px   - Small tablets
md: 768px   - Tablets
lg: 1024px  - Desktops
xl: 1280px  - Large desktops
```

### Layout Changes

**Stats Cards**:
- Mobile: 1 column
- Tablet: 2 columns
- Desktop: 4 columns

**Platform Configurator**:
- Mobile: 1 column (stacked)
- Desktop: 2 columns (sidebar + form)

**Listings**:
- Always full width with scroll

---

## Loading States

### Skeleton Loading
```
┌────────────────────────────┐
│ ▄▄▄▄▄▄▄▄▄▄▄▄▄▄            │  ← Pulsing gray rectangles
│ ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄        │
└────────────────────────────┘
```

**Used for**:
- Stats cards while loading
- Listings while loading

### Spinner
```
  ⟳  Loading...
```

**Used for**:
- Button actions (Test, Save)
- Form submissions

---

## Animations

### Transitions
```css
/* Default */
transition: all 0.2s ease-in-out;

/* Hover effects */
- Shadow increase
- Background color change
- Scale transform (1.02)
```

### Skeleton Pulse
```css
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
```

---

## Accessibility

### Focus States
- All interactive elements have visible focus rings
- Color: Blue (#93c5fd)
- Width: 2px

### Color Contrast
- Text on white: Minimum 4.5:1 ratio
- Buttons: Minimum 3:1 ratio
- Platform badges: Minimum 4.5:1 ratio

### Keyboard Navigation
- Tab order follows visual order
- Enter triggers primary actions
- Escape closes modals/dropdowns

---

## Icons

**Using Emoji** (no icon library):
```
🚗 - Car/Logo
📊 - Statistics
🆕 - New
🌐 - Platforms
🕒 - Time
🔧 - Configure
📋 - Listings
🔔 - Notifications
📱 - Telegram
💬 - Discord
📧 - Email
🧪 - Test
💾 - Save
🔄 - Loading
✅ - Success
❌ - Error
📍 - Location
🟢 - Status (online)
🔴 - Status (offline)
```

---

## Implementation Notes

1. **Tailwind Classes**: All styling uses Tailwind utility classes
2. **Custom Classes**: Minimal custom CSS (see `globals.css`)
3. **Responsive**: Mobile-first approach
4. **Performance**: Lazy load images, debounce API calls
5. **SEO**: Semantic HTML, proper heading hierarchy

---

**Design System Complete! 🎨**
