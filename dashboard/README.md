# DeckBrain Dashboard

Map-focused Next.js dashboard for visualizing fishing vessel trip data from the DeckBrain Core API.

## Features

- **Map-Centric Interface**: Interactive Leaflet map displaying trip tracks and tow boundaries
- **Trip List**: Sidebar showing all trips with key metadata (duration, distance)
- **Plotter-Agnostic**: Works with normalized data from any supported plotter (Olex, MaxSea, etc.)
- **GeoJSON Visualization**: Displays trip tracks and depth data on marine charts
- **Responsive Design**: Clean, nautical-themed UI optimized for clarity

## Prerequisites

- Node.js 18+ and npm
- DeckBrain Core API running at `http://localhost:8000`
- Mock trip data seeded in Core API database

## Setup

1. **Install dependencies:**
   ```bash
   cd dashboard
   npm install
   ```

2. **Configure environment (optional):**
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local if needed
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Open dashboard:**
   Navigate to `http://localhost:3000`

## Architecture

```
dashboard/
  app/              - Next.js app router
    trips/          - Trips page (main view)
    layout.tsx      - Root layout
    globals.css     - Global styles with Tailwind
  core/             - Shared utilities
    api/            - API client for Core API
      client.ts     - API functions
      types.ts      - TypeScript interfaces
    config.ts       - Configuration (API URL, device ID)
  features/         - Feature modules
    trips/          - Trips feature
      components/   - Trip-specific components
        MapView.tsx - Leaflet map component
        TripList.tsx - Trip list sidebar
```

## Configuration

Environment variables (`.env.local`):

- `NEXT_PUBLIC_API_URL` - Core API URL (default: `http://localhost:8000`)
- `NEXT_PUBLIC_DEFAULT_DEVICE_ID` - Device ID for testing (default: `test-vessel-001`)

## Usage

1. **Ensure Core API is running:**
   ```bash
   cd ../core-api
   uvicorn app.main:app --reload
   ```

2. **Seed mock data (if not already done):**
   ```bash
   cd ../core-api
   python scripts/seed_mock_trips.py
   ```

3. **Start dashboard:**
   ```bash
   npm run dev
   ```

4. **View trips:**
   - Select a trip from the sidebar
   - Map will display the trip track as a blue line
   - Tow boundaries (if any) shown as orange lines
   - Click track for details (time, depth, etc.)

## Development

- **Hot reload**: Changes auto-reload in dev mode
- **TypeScript**: Full type safety with Core API responses
- **Tailwind CSS**: Utility-first styling with custom nautical theme
- **Leaflet**: Map library for track visualization

## Building for Production

```bash
npm run build
npm start
```

## Troubleshooting

**"Failed to fetch trips" error:**
- Ensure Core API is running at the configured URL
- Check that migrations are applied: `alembic upgrade head`
- Verify mock data is seeded: `python scripts/seed_mock_trips.py`

**Map not displaying:**
- Check browser console for errors
- Leaflet requires client-side rendering (already configured with `dynamic` import)

**No trips in sidebar:**
- Run seed script to create mock trips
- Check Core API is accessible at `http://localhost:8000`

## Status

**Implemented:**
- Trip list with metadata display
- Interactive map with Leaflet
- GeoJSON track visualization
- Trip selection and track loading
- Error handling and loading states
- Responsive layout

**Future:**
- Live status view
- History/coverage layers
- Tow notes panel
- User authentication
- Multi-device support
