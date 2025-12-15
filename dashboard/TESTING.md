# Testing the DeckBrain Dashboard

Step-by-step guide to test the dashboard with the Core API.

## Prerequisites Check

### 1. Verify Core API is Running

Open a terminal and check:

```bash
# Navigate to core-api
cd core-api

# Activate virtual environment (if needed)
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# OR
venv\Scripts\activate  # Windows CMD

# Start Core API server
uvicorn app.main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Test API is working:**
Open browser: `http://localhost:8000/docs`
- Should see Swagger UI
- Try `GET /api/trips?device_id=test-vessel-001`
- Should return list of trips

### 2. Verify Mock Data is Seeded

```bash
# In core-api directory
python scripts/seed_mock_trips.py
```

**Expected output:**
```
🌱 Seeding mock trip data...
  Found existing device: test-vessel-001
  Creating mock trips...
    ✓ Created trip: Morning Trip - Dec 10 with 2 tows
    ✓ Created trip: Afternoon Trip - Dec 11 with 1 tow
    ✓ Created trip: Recent Trip - Yesterday with 1 tow
✅ Mock data seeded successfully!
```

## Step 2: Install Dashboard Dependencies

Open a **new terminal** (keep Core API running):

```bash
# Navigate to dashboard
cd dashboard

# Install dependencies (first time only)
npm install
```

**Expected output:**
```
added 500+ packages
```

## Step 3: Start Dashboard

```bash
# Still in dashboard directory
npm run dev
```

**Expected output:**
```
  ▲ Next.js 15.x.x
  - Local:        http://localhost:3000
  - Ready in X seconds
```

## Step 4: Open Dashboard

Open browser: `http://localhost:3000`

**What you should see:**
- **Left sidebar**: "DeckBrain" header with "Trip Dashboard"
- **Trip list**: 3 trips listed (Morning Trip, Afternoon Trip, Recent Trip)
- **Right side**: Map with welcome message ("Select a trip from the sidebar")

## Step 5: Test Trip Selection

1. **Click on a trip** in the sidebar (e.g., "Morning Trip - Dec 10")
   - Trip should highlight (blue border)
   - Loading spinner appears briefly
   - Map should display the trip track as a **blue line**

2. **Interact with the map:**
   - **Zoom**: Mouse wheel or +/- buttons
   - **Pan**: Click and drag
   - **Click track line**: Popup shows trip details (start time, end time, points count)
   - **Start marker**: Green circle (trip start)
   - **End marker**: Red circle (trip end)

3. **Select different trip:**
   - Click another trip in sidebar
   - Map updates to show new track
   - Track info panel (top-right) updates

## Step 6: Test Features

### Test Trip List
- ✅ All 3 trips visible
- ✅ Trip names, dates, duration, distance shown
- ✅ Selected trip highlighted
- ✅ Clicking trip updates map

### Test Map
- ✅ Track displayed as blue LineString
- ✅ Map centers on track automatically
- ✅ Start/end markers visible
- ✅ Popups work when clicking track
- ✅ Map is interactive (zoom, pan)

### Test Error Handling
- **Stop Core API** (Ctrl+C in API terminal)
- **Refresh dashboard**
- Should see error message: "Error loading trips"
- **Restart Core API** and refresh - should work again

## Troubleshooting

### "Failed to fetch trips" Error

**Check:**
1. Core API is running: `http://localhost:8000/docs` should work
2. Correct API URL in dashboard config (default: `http://localhost:8000`)
3. CORS is enabled in Core API (should be by default)

**Fix:**
```bash
# Restart Core API
cd core-api
uvicorn app.main:app --reload
```

### No Trips in Sidebar

**Check:**
1. Mock data is seeded: Run `python scripts/seed_mock_trips.py`
2. Device ID matches: Default is `test-vessel-001`
3. Database has trips: Check `core-api/dev.db` exists

**Fix:**
```bash
cd core-api
python scripts/seed_mock_trips.py
```

### Map Not Displaying

**Check:**
1. Browser console for errors (F12)
2. Leaflet CSS is loading (check Network tab)
3. No ad blockers blocking map tiles

**Fix:**
- Clear browser cache
- Try different browser
- Check console for specific errors

### "Module not found" Errors

**Fix:**
```bash
cd dashboard
rm -rf node_modules package-lock.json
npm install
```

### Port Already in Use

**Fix:**
```bash
# Use different port
npm run dev -- -p 3001
```

Then open: `http://localhost:3001`

## Expected Behavior

### Successful Test Flow:

1. ✅ Dashboard loads at `http://localhost:3000`
2. ✅ Sidebar shows 3 trips
3. ✅ Clicking trip loads track on map
4. ✅ Map shows blue track line
5. ✅ Start (green) and end (red) markers visible
6. ✅ Clicking track shows popup with details
7. ✅ Selecting different trip updates map
8. ✅ No console errors

## Testing Checklist

- [ ] Core API running (`http://localhost:8000/docs` works)
- [ ] Mock data seeded (3 trips exist)
- [ ] Dashboard starts (`npm run dev` succeeds)
- [ ] Dashboard loads in browser
- [ ] Trip list shows 3 trips
- [ ] Can select trips
- [ ] Map displays tracks
- [ ] Map is interactive (zoom, pan)
- [ ] Popups work
- [ ] Start/end markers visible
- [ ] Error handling works (stop API, see error)
- [ ] No console errors

## Next Steps After Testing

Once everything works:
- ✅ v0.2 is complete!
- Ready for v0.3 (Tow Notes) or real parsing implementation
- Dashboard is production-ready for mock data

