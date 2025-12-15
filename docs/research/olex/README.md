# Olex File Format Research

This document guides the process of understanding Olex file formats to implement real parsing in DeckBrain.

## Status

⚠️ **Research Phase** - Waiting for sample files from actual Olex systems.

## What Files to Export / Where to Find Them

Olex stores navigation and fishing data in various file formats:

- **Track files**: Usually stored in specific Olex export directories
- **Depth/sounding data**: May be in separate files or embedded in track files
- **Marks/waypoints**: Exported separately or included in backup files
- **Project files**: Complete backups that may contain all of the above

**Expected export locations:**
- Olex data directory (Linux/Windows)
- USB export locations configured by user
- Network share locations if configured

**Questions:**
- What is the default export directory path on Olex systems?
- Can Olex auto-export on a schedule?
- What export formats does Olex support (CSV, binary, proprietary)?

## Sample File Checklist

When we receive Olex sample files, record the following for each file:

### File Properties
- [ ] Filename(s) and extension(s)
- [ ] File size(s)
- [ ] Is the file text or binary?
- [ ] If text: what encoding? (UTF-8, ASCII, Latin-1?)
- [ ] If text: what line endings? (CRLF, LF?)
- [ ] If text: what field separator? (comma, tab, space, pipe?)
- [ ] If binary: are there any magic bytes or headers?
- [ ] If archive/zip: what is the internal folder structure?

### Timestamp Information
- [ ] How are dates formatted? (ISO8601, Unix timestamp, custom?)
- [ ] How are times formatted? (24h, 12h, decimal hours?)
- [ ] What timezone is used? (UTC, local, vessel time?)
- [ ] Are timestamps in filename or inside the file?
- [ ] How precise are timestamps? (seconds, milliseconds?)

### Geographic Coordinates
- [ ] What coordinate format? (decimal degrees, degrees/minutes/seconds, degrees decimal minutes?)
- [ ] What datum? (WGS84, NAD83, other?)
- [ ] Latitude range and format (N/S designation or +/-)
- [ ] Longitude range and format (E/W designation or +/-)
- [ ] How many decimal places?

### Depth and Sounding Data
- [ ] What depth units? (meters, feet, fathoms?)
- [ ] How precise are depth readings? (decimal places)
- [ ] Are soundings timestamped?
- [ ] Are soundings tied to coordinates?
- [ ] Any water temperature data?
- [ ] Any speed/course data?
- [ ] Any sonar frequency or gain settings?

### File Structure and Format
- [ ] Is there a header row or metadata section?
- [ ] How many columns/fields per record?
- [ ] Are there section markers or delimiters?
- [ ] Are multiple data types mixed in one file?
- [ ] Any footer or checksum data?

## Questions to Answer (Mapping to DeckBrain Entities)

### Trips
**How do we infer trip boundaries from Olex files?**
- [ ] Are trips explicitly marked in Olex files?
- [ ] Do we infer trips from time gaps in track data? (e.g., gap > 4 hours = new trip)
- [ ] Are there project files or session files that define trips?
- [ ] Can we use "power on/off" events if available?

**What trip metadata is available?**
- [ ] Trip names or identifiers?
- [ ] Trip start/end times?
- [ ] Trip summaries (distance, duration)?

### Tows
**How do we identify tow segments within a trip?**
- [ ] Are tows explicitly marked by the user in Olex?
- [ ] Do we infer tows from speed changes? (e.g., speed < 3 knots = towing)
- [ ] Are there depth pattern changes that indicate towing?
- [ ] Are tow markers saved in a separate file?

**What tow metadata is available?**
- [ ] Tow names or numbers?
- [ ] Tow start/end markers?
- [ ] Gear type information?

### Soundings
**How do we extract individual depth readings?**
- [ ] Are soundings in a separate file from track data?
- [ ] What is the sounding frequency? (every second, every 10 seconds, variable?)
- [ ] Do soundings always have coordinates?
- [ ] Do soundings always have timestamps?

**What sounding metadata is available?**
- [ ] Depth value and units
- [ ] Latitude and longitude
- [ ] Timestamp
- [ ] Water temperature
- [ ] Speed over ground
- [ ] Course over ground
- [ ] Bottom type or hardness (if available)

### Marks
**How are waypoints and fishing marks stored?**
- [ ] Are marks in a separate file?
- [ ] What mark types does Olex support?
- [ ] How are mark names/labels stored?
- [ ] Are mark icons or colors specified?
- [ ] Are marks grouped or categorized?

**What mark metadata is available?**
- [ ] Mark name
- [ ] Coordinates
- [ ] Mark type or category
- [ ] Creation timestamp
- [ ] User notes or descriptions

## How to Use This Document

1. **Drop sample Olex files** into `samples/olex/` directory.
2. **Run the inspection tool**:
   ```bash
   python scripts/inspect_plotter_file.py samples/olex
   ```
3. **Fill out the checklist above** based on inspection tool output and manual review.
4. **Update this document** with findings.
5. **Design the OlexParser** implementation based on documented file format.

## References

- Olex official documentation (if available)
- User manuals for Olex export features
- Community forums or guides
- Direct communication with Olex users

## Next Steps

Once sample files are available and analyzed:
1. Update `modules/ingestion/parsers/olex.py` with real parsing logic
2. Create unit tests with sanitized sample data
3. Test end-to-end ingestion pipeline
4. Verify trips, tows, soundings are correctly extracted
5. Update processing_status from `parsed_stub` to `processed`

