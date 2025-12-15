# Plotter Format Research

This directory contains research documentation for understanding plotter file formats before implementing real parsing.

## Purpose

DeckBrain's ingestion pipeline currently uses stub parsers that validate file receipt but don't extract data. Before implementing real parsing logic, we need to:

1. **Understand file formats**: Analyze actual plotter exports to understand structure, encoding, and data layout
2. **Document findings**: Record observations in vendor-specific research docs
3. **Design parsers**: Use documented findings to implement robust, well-tested parsers

## Vendor-Specific Research

- **[Olex](olex/README.md)**: Research documentation for Olex file formats
- **[MaxSea TimeZero](maxsea/README.md)**: Research documentation for MaxSea file formats

Each vendor directory contains:
- Comprehensive file format checklist
- Questions to answer for DeckBrain entity mapping (trips, tows, soundings, marks)
- Instructions for using the inspection tool
- References and next steps

## How to Use

### 1. Obtain Sample Files

Work with vessel operators to obtain representative sample files:
- Small files (< 1 MB) are easiest to analyze
- Multiple file types (tracks, marks, backups) provide complete picture
- Sanitize data if needed (remove sensitive vessel identifiers)

**Important**: Never commit real vessel data to the repository. Sample files are gitignored.

### 2. Drop Samples

Place sample files in the appropriate directory:
```
samples/olex/      - Olex sample files
samples/maxsea/    - MaxSea sample files
```

These directories are gitignored to prevent accidental commits of sensitive data.

### 3. Run Inspection Tool

Use the inspection tool to analyze file structure:

```bash
# Inspect all files in a directory
python scripts/inspect_plotter_file.py samples/olex

# Inspect a single file
python scripts/inspect_plotter_file.py samples/olex/track_data.txt

# Inspect ZIP archive contents
python scripts/inspect_plotter_file.py samples/maxsea/backup.zip --extract
```

The tool reports:
- File size and SHA256 hash
- Text vs binary classification
- First 32 bytes (hex dump)
- Text encoding detection
- Text preview (first 20 lines)
- ZIP archive contents

### 4. Document Findings

Update the vendor-specific README with findings:
- Fill out the sample file checklist
- Answer entity mapping questions
- Document coordinate formats, timestamp formats, depth units, etc.
- Record any unexpected patterns or edge cases

### 5. Design Parser

Use documented findings to implement the parser:
- Update `core-api/modules/ingestion/parsers/<vendor>.py`
- Replace stub implementation with real parsing logic
- Extract trips, tows, soundings, marks from raw files
- Handle edge cases and errors gracefully
- Update `processing_status` from `parsed_stub` to `processed`

### 6. Test End-to-End

Verify the full ingestion pipeline:
1. Upload sample file via API
2. Verify auto-ingestion triggers (in dev mode)
3. Check `file_records.processing_status` updates correctly
4. Verify trips, tows, soundings are created in database
5. Test trip and track API endpoints
6. Visualize tracks on dashboard

## Inspection Tool

The inspection tool (`scripts/inspect_plotter_file.py`) is a lightweight utility for understanding unknown file formats:

**Features:**
- File type detection (text, binary, ZIP, etc.)
- SHA256 hash computation for integrity verification
- Hex dump of first bytes (useful for identifying magic bytes)
- Text encoding detection (UTF-8, ASCII, Windows-1252, etc.)
- Safe text preview with encoding error handling
- ZIP archive inspection (list contents without extraction)
- Recursive directory inspection

**No Parsing:**
- The tool does NOT parse files or extract structured data
- It only reports file characteristics to help understand structure
- Real parsing logic goes in vendor-specific parser classes

## Current Status

**Olex**: Research phase - awaiting sample files  
**MaxSea**: Research phase - awaiting sample files

## Next Steps

Once sample files are analyzed and parsers implemented:
1. Remove stub logic from parser classes
2. Update ingestion pipeline documentation
3. Create unit tests with sanitized sample data
4. Update API documentation with real data examples
5. Test with dashboard for visual verification

## References

- [Ingestion Pipeline Documentation](../engineering/ingestion_pipeline.md)
- [Database Schema](../db_schema.md)
- [API Specification](../api_spec.md)

