# Platform Criteria Specificaties

## Per Platform: Optimale Criteria

### 1. Marktplaats.nl
**URL Parameters:**
- `query` - Zoekwoorden (string)
- `priceFrom` / `priceTo` - Prijs range (integer)
- `yearFrom` / `yearTo` - Bouwjaar (integer)
- `mileageTo` - Max kilometerstand (integer)
- `postcode` - Postcode (string, 4 digits)
- `distanceMeters` - Afstand in meters (integer)
- `categoryId` - Categorie (default: auto's)

**Beste Aanpak:**
- Dropdown voor categorie
- Text input voor keywords
- Sliders voor prijs & jaar
- Number input voor km-stand
- Optioneel: Locatie filter

---

### 2. AutoScout24
**URL Parameters:**
- `make` / `model` - Merk & Model (dropdown selectie)
- `pricefrom` / `priceto` - Prijs range
- `fregfrom` / `fregto` - Registratiejaar
- `kmto` - Max kilometers
- `fuel` - Brandstof type (D=Diesel, B=Benzine, E=Electric, H=Hybrid)
- `gear` - Versnelling (M=Manual, A=Automatic)
- `power` - Vermogen in PK

**Beste Aanpak:**
- **Cascading dropdowns**: Eerst merk, dan model
- Radio buttons voor brandstof
- Checkboxes voor transmissie
- Sliders voor prijs, jaar, km

---

### 3. Mobile.de
**URL Parameters:**
- `makeModelVariant1.makeId` - Merk ID (code)
- `makeModelVariant1.modelDescription` - Model naam
- `minPrice` / `maxPrice` - Prijs
- `minFirstRegistrationDate` / `maxFirstRegistrationDate` - Jaar
- `maxMileage` - Max kilometers
- `zipCode` - Postcode (Duits)
- `scopeId` - Zoekradius in km

**Beste Aanpak:**
- Merk dropdown met codes mapping
- Model autocomplete
- Duitse postcode input
- Radius slider

---

### 4. eBay Kleinanzeigen
**RSS Parameters:**
- `keywords` - Zoekwoorden in URL path
- `category` - Categorie ID (216 = Auto's)
- `priceFrom:priceTo` - In URL path format
- `zipCode` - Duitse postcode
- `radius` - Radius in km

**Beste Aanpak:**
- Eenvoudige keyword search
- Prijs range sliders
- Optionele locatie filter
- **Voordeel: RSS = meest betrouwbaar!**

---

### 5. Facebook Marketplace (Experimenteel)
**Parameters:**
- `query` - Vrije tekst zoekterm
- `minPrice` / `maxPrice` - Prijs
- `location` - Locatie naam
- `radius` - Radius in km

**Beste Aanpak:**
- Simple search box
- Prijs range
- Location autocomplete
- **Waarschuwing banner**: "Experimenteel, gebruik op eigen risico"

---

## 🎨 UI/UX Aanbevelingen

### Form Design Per Platform
```
┌─────────────────────────────────┐
│ Platform Selector (Tabs)        │
├─────────────────────────────────┤
│ [Marktplaats] [AutoScout] [etc] │
├─────────────────────────────────┤
│                                 │
│  Platform-Specifieke Form       │
│  - Sliders voor prijs/jaar      │
│  - Dropdowns voor merk/model    │
│  - Toggle voor optionele fields │
│                                 │
│  [Preview Search URL]           │
│                                 │
│  [ Test Scrape ]  [ Save ]      │
└─────────────────────────────────┘
```

### Features:
1. **Live Preview** - Toon gebouwde URL
2. **Test Button** - Direct testen zonder opslaan
3. **Results Preview** - Laat eerste 5 resultaten zien
4. **Schedule Config** - Check interval per platform
5. **Notification Settings** - Telegram/Discord/Email toggle

