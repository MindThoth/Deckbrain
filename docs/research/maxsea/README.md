# MaxSea TimeZero File Format Research

This document guides the process of understanding MaxSea TimeZero file formats to implement real parsing in DeckBrain.

## Status

⚠️ **Research Phase** - Waiting for sample files from actual MaxSea TimeZero systems.

## What Files to Export / Where to Find Them

MaxSea TimeZero stores data in various formats:

- **Track files (.mf2, .tz)**: GPS tracks and navigation history
- **Backup files**: Complete system backups containing all data
- **Export files**: User-exported data in various formats (CSV, GPX, KML)
- **Mark/waypoint files**: Saved marks and waypoints
- **Route files**: Planned routes and navigation data

**Expected export locations:**
- MaxSea TimeZero data directory (Windows)
- User Documents folder (e.g., `C:\Users\<user>\Documents\MaxSea TimeZero\`)
- Custom export directories configured by user
- Backup locations on USB drives or network shares

**Questions:**
- What is the default MaxSea data directory path?
- Can MaxSea auto-export on a schedule?
- What export formats does MaxSea support (CSV, GPX, KML, proprietary)?
- Are there different file formats between MaxSea versions (TZ Classic vs TZ Professional)?

## Sample File Checklist

When we receive MaxSea sample files, record the following for each file:

### File Properties
- [ ] Filename(s) and extension(s) (.mf2, .tz, .csv, .gpx, .zip, etc.)
- [ ] File size(s)
- [ ] Is the file text, binary, or compressed?
- [ ] If text: what encoding? (UTF-8, ASCII, Windows-1252?)
- [ ] If text: what line endings? (CRLF expected for Windows)
- [ ] If text: what field separator? (comma, semicolon, tab?)
- [ ] If binary: are there magic bytes or file signatures?
- [ ] If compressed/zip: what is the internal structure?
- [ ] MaxSea version that created the file?

### Timestamp Information
- [ ] How are dates formatted? (ISO8601, MM/DD/YYYY, DD/MM/YYYY, custom?)
- [ ] How are times formatted? (24h, 12h, decimal hours?)
- [ ] What timezone is used? (UTC, local, vessel time?)
- [ ] Are timestamps embedded in filenames?
- [ ] How precise are timestamps? (seconds, milliseconds?)
- [ ] Is there a "recorded time" vs "vessel time" distinction?

### Geographic Coordinates
- [ ] What coordinate format? (decimal degrees, DMS, DMM?)
- [ ] What datum? (WGS84 is standard, but confirm)
- [ ] Latitude format (N/S designation, +/-, or other?)
- [ ] Longitude format (E/W designation, +/-, or other?)
- [ ] How many decimal places for precision?
- [ ] Any coordinate system metadata in files?

### Depth and Sounding Data
- [ ] What depth units? (meters, feet, fathoms?)
- [ ] Depth precision (decimal places)
- [ ] Are soundings separate from track data?
- [ ] Are soundings timestamped?
- [ ] Are soundings tied to GPS coordinates?
- [ ] Water temperature data available?
- [ ] Speed over ground / course over ground?
- [ ] Sounder settings (frequency, range, gain)?
- [ ] Bottom hardness or classification?

### File Structure and Format
- [ ] Is there a file header or metadata section?
- [ ] How many fields per record?
- [ ] Are there section markers (e.g., [TRACKS], [MARKS])?
- [ ] Are different data types in separate files or mixed?
- [ ] Is there a schema or format version indicator?
- [ ] Any CRC or checksum for integrity?
- [ ] Are comments or user notes included?

## Questions to Answer (Mapping to DeckBrain Entities)

### Trips
**How do we infer trip boundaries from MaxSea files?**
- [ ] Are trips explicitly defined in MaxSea?
- [ ] Do we infer trips from time gaps in track data? (e.g., gap > 4 hours = new trip)
- [ ] Are there "log start/end" markers?
- [ ] Can we use system on/off events?
- [ ] Are different trips stored in separate files?

**What trip metadata is available?**
- [ ] Trip names or identifiers?
- [ ] Trip start/end timestamps?
- [ ] Total distance and duration?
- [ ] Vessel name or ID?

### Tows
**How do we identify tow segments within a trip?**
- [ ] Are tows explicitly marked by users in MaxSea?
- [ ] Do we infer tows from speed/course changes? (e.g., speed < 4 knots and consistent course = towing)
- [ ] Are there depth profile patterns that indicate towing?
- [ ] Are tow markers saved with GPS coordinates?
- [ ] Can users add notes or markers for tow start/end?

**What tow metadata is available?**
- [ ] Tow names or numbers?
- [ ] Tow start/end positions and times?
- [ ] Gear type or fishing method?
- [ ] User-entered notes?

### Soundings
**How do we extract individual depth readings?**
- [ ] Are soundings in separate files (.tz, .mf2) or embedded in track files?
- [ ] What is the sounding recording frequency? (every second, every N seconds, variable?)
- [ ] Do soundings always include GPS coordinates?
- [ ] Do soundings always include timestamps?
- [ ] Are there sounding gaps or interpolated values?

**What sounding metadata is available?**
- [ ] Depth value and units
- [ ] Latitude and longitude
- [ ] Timestamp
- [ ] Water temperature
- [ ] Speed over ground
- [ ] Course over ground
- [ ] Sounder frequency (50 kHz, 200 kHz, CHIRP, etc.)
- [ ] Bottom classification or hardness (if equipped)

### Marks
**How are waypoints and fishing marks stored?**
- [ ] Are marks stored in separate files?
- [ ] What mark types does MaxSea support? (waypoints, MOB, fishing marks, etc.)
- [ ] How are mark names/labels stored?
- [ ] Are mark icons or colors specified?
- [ ] Can marks be organized into groups or categories?

**What mark metadata is available?**
- [ ] Mark name or label
- [ ] Coordinates (lat/lon)
- [ ] Mark type or category
- [ ] Creation timestamp
- [ ] User comments or descriptions
- [ ] Mark color or icon ID

## How to Use This Document

1. **Drop sample MaxSea files** into `samples/maxsea/` directory.
2. **Run the inspection tool**:
   ```bash
   python scripts/inspect_plotter_file.py samples/maxsea
   ```
3. **Fill out the checklist above** based on inspection tool output and manual review.
4. **Update this document** with findings.
5. **Design the MaxSeaParser** implementation based on documented file format.

## References

- MaxSea TimeZero official documentation
- User manual for data export features
- Community forums or user groups
- Direct communication with MaxSea users
- File format specifications (if publicly available)

## Known File Types

Based on research and community knowledge:

- **`.mf2`**: MaxSea binary format (legacy format, still supported)
- **`.tz`**: TimeZero proprietary format (current version)
- **`.gpx`**: GPX export (XML-based, standard GPS format)
- **`.csv`**: CSV export (user-initiated export)
- **`.kml`/`.kmz`**: Google Earth export
- **Backup files**: May be ZIP archives containing multiple file types

## Next Steps

Once sample files are available and analyzed:
1. Update `modules/ingestion/parsers/maxsea.py` with real parsing logic
2. Handle multiple MaxSea file formats (.mf2, .tz, .gpx, etc.)
3. Create unit tests with sanitized sample data
4. Test end-to-end ingestion pipeline
5. Verify trips, tows, soundings are correctly extracted
6. Update processing_status from `parsed_stub` to `processed`

