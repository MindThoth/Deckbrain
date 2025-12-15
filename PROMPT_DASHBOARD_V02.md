# Prompt: Build Dashboard for v0.2 Trips Vertical Slice

You are my AI coding assistant working in the DeckBrain repo.
Use the Claude Sonnet 4.5 model for all coding and architectural decisions.

Goal:
Build the Next.js Dashboard for DeckBrain (v0.2.x-dev): a map-focused web interface that displays trips and tracks from the Core API. This completes the v0.2 "Trips Vertical Slice" by providing a visual frontend for the trips data.

This dashboard must:
- Display trips from the Core API
- Show trip tracks on an interactive map
- Be plotter-agnostic (works with data from any plotter)
- Use modern, clean UI/UX
- Follow the core + modules pattern
- Update DEVLOG.md
- Do NOT update CHANGELOG.md

Key principles:
- Map-centric design (captains think in maps)
- Plotter-agnostic (normalized data from Core API)
- Simple, intuitive navigation
- No real authentication yet (dev mode)
- Clean, maintainable code structure

====================================================
STEP 0 — Read context (MANDATORY)
====================================================

Read carefully:
- DECKBRAIN_FOUNDATION.md
- PROJECT_GUIDE.md
- docs/api_spec.md (trips endpoints)
- core-api/README.md
- DEVLOG.md (latest entry)

Understand:
- Core API provides trips endpoints at /api/trips
- Track data is GeoJSON format
- Dashboard should be plotter-agnostic
- Map-centric design is key

====================================================
STEP 1 — Initialize Next.js project
====================================================

In the `dashboard/` directory:

1. Initialize Next.js with TypeScript:
   ```bash
   npx create-next-app@latest . --typescript --tailwind --app --no-src-dir
   ```

2. Install additional dependencies:
   - `leaflet` and `react-leaflet` (or `mapbox-gl` and `react-map-gl`)
   - `axios` or `fetch` for API calls
   - `date-fns` for date formatting

3. Create directory structure:
   ```
   dashboard/
     app/              - Next.js app router
       (trips)/        - Trips page route
       layout.tsx      - Root layout
       page.tsx        - Home/redirect
     core/             - Shared utilities
       api/            - API client
       components/     - Shared components
       lib/            - Utilities
     features/         - Feature modules
       trips/          - Trips feature
         components/   - Trip-specific components
         hooks/        - Custom hooks
     public/           - Static assets
   ```

4. Configure Tailwind for marine/chart styling

====================================================
STEP 2 — Create API client
====================================================

In `dashboard/core/api/client.ts`:

Create a simple API client that:
- Base URL: `http://localhost:8000` (configurable)
- Functions for:
  - `getTrips(deviceId: string)` → calls GET /api/trips
  - `getTripDetail(tripId: number)` → calls GET /api/trips/{trip_id}
  - `getTripTrack(tripId: number, includeTows?: boolean)` → calls GET /api/trips/{trip_id}/track
  - `getTowTrack(tripId: number, towId: number)` → calls GET /api/trips/{trip_id}/tows/{tow_id}/track

Use TypeScript interfaces matching the API responses.

====================================================
STEP 3 — Build trips page structure
====================================================

In `dashboard/app/(trips)/page.tsx`:

Create the trips page with:
- Layout: Sidebar (left) + Map (right)
- Sidebar:
  - Trip list (from API)
  - Trip selection
  - Basic trip info (name, date, duration)
- Map:
  - Interactive map (Leaflet or Mapbox)
  - Display selected trip track as GeoJSON LineString
  - Optional: Show tow boundaries if available

Use responsive design (sidebar collapses on mobile).

====================================================
STEP 4 — Implement map component
====================================================

In `dashboard/features/trips/components/MapView.tsx`:

Create a map component that:
- Initializes map with appropriate center/zoom
- Accepts GeoJSON track data as prop
- Renders LineString track on map
- Shows trip start/end markers
- Optional: Depth color-coding or elevation profile

Use Leaflet (simpler) or Mapbox (more features).

For Leaflet, use:
- `react-leaflet` for React integration
- Marine chart tile layer (OpenStreetMap or nautical charts)
- Custom styling for track lines

====================================================
STEP 5 — Implement trip list sidebar
====================================================

In `dashboard/features/trips/components/TripList.tsx`:

Create sidebar component that:
- Fetches trips from API on mount
- Displays list of trips (name, date, duration)
- Highlights selected trip
- Handles trip selection (updates map)
- Shows loading state
- Handles errors gracefully

Use a clean, simple list design.

====================================================
STEP 6 — Connect components
====================================================

Wire everything together:

1. Trips page fetches trip list on mount
2. User selects trip → fetches track data
3. Track data passed to map component
4. Map displays track as LineString
5. Optional: Show trip details panel

Handle loading and error states throughout.

====================================================
STEP 7 — Styling and UX
====================================================

Apply clean, marine-focused styling:

- Color scheme: Blues, grays (ocean/nautical theme)
- Typography: Clear, readable fonts
- Map styling: Nautical chart appearance if possible
- Responsive: Works on desktop and tablet
- Loading states: Skeleton loaders or spinners
- Error states: Clear error messages

Keep it simple and functional (captains need clarity, not flashy UI).

====================================================
STEP 8 — Configuration
====================================================

Add configuration:

1. Create `dashboard/core/config.ts`:
   - API base URL (default: `http://localhost:8000`)
   - Device ID for testing (default: `test-vessel-001`)
   - Environment variables support

2. Create `.env.local.example`:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_DEFAULT_DEVICE_ID=test-vessel-001
   ```

====================================================
STEP 9 — Testing
====================================================

Verify:
- Dashboard starts without errors
- Can fetch trips from Core API
- Map displays trip tracks correctly
- Trip selection updates map
- Responsive design works
- Error handling works (API down, no trips, etc.)

Test with mock data from Core API (run seed script first).

====================================================
STEP 10 — Documentation
====================================================

Update or create:

1. `dashboard/README.md`:
   - Setup instructions
   - How to run dev server
   - Configuration options
   - Architecture overview

2. Update `DEVLOG.md`:
   - Add entry for dashboard implementation
   - Note that v0.2 is now complete

Do NOT modify CHANGELOG.md.

====================================================
STEP 11 — DEVLOG entry (REQUIRED)
====================================================

Append to DEVLOG.md:

### YYYY-MM-DD – v0.2.x-dev – branch: BRANCH_NAME
- Model: Cursor (Claude Sonnet 4.5)
- Changes:
  - Built Next.js dashboard with trips visualization.
  - Implemented map component with Leaflet/Mapbox for track display.
  - Created trip list sidebar with API integration.
  - Connected dashboard to Core API trips endpoints.
  - Added responsive layout and marine-focused styling.
- Notes:
  - v0.2 Trips Vertical Slice is now complete (Core API + Dashboard).
  - Dashboard displays mock trip data from Core API.
  - Ready for real trip data when parsing is implemented.

====================================================
STEP 12 — Sanity checks
====================================================

Confirm:
- Dashboard runs: `npm run dev`
- Can see trips in sidebar
- Map displays tracks when trip selected
- No console errors
- Responsive design works
- Code follows Next.js best practices

Finally, print a short summary describing:
- Dashboard architecture
- How trips are fetched and displayed
- Map integration approach
- What's ready for v0.3

