# Dashboard Setup Instructions

Quick guide to get the DeckBrain Dashboard running.

## Prerequisites

1. **Node.js 18+** installed
2. **Core API running** at `http://localhost:8000`
3. **Mock data seeded** in Core API

## Setup Steps

### 1. Install dependencies
```bash
cd dashboard
npm install
```

### 2. Start dev server
```bash
npm run dev
```

### 3. Open dashboard
Navigate to: `http://localhost:3000`

You should see:
- Sidebar with list of trips
- Map (select a trip to see its track)

## Troubleshooting

**"Failed to fetch trips" error:**
- Make sure Core API is running: `cd core-api && uvicorn app.main:app --reload`
- Check Core API is accessible at http://localhost:8000
- Verify seed data exists: `cd core-api && python scripts/seed_mock_trips.py`

**No trips in sidebar:**
- Seed mock data: `cd core-api && python scripts/seed_mock_trips.py`

**Map not showing:**
- Check browser console for errors
- Leaflet CSS should load automatically

## Next Steps

- Select a trip from sidebar
- Map will display the trip track
- Click on track lines for details
- Start/end markers show trip boundaries

## Configuration

Create `.env.local` to customize:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_DEFAULT_DEVICE_ID=test-vessel-001
```

See `.env.local.example` for all options.

