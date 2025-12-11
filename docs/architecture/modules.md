# Module Structure

DeckBrain uses a core + modules pattern for each service. See `DECKBRAIN_FOUNDATION.md` for the complete explanation; this file will hold additional module-specific details as they are defined.

## Multi-Plotter Architecture

DeckBrain supports multiple plotter vendors (Olex, MaxSea, and others) through vendor-specific connector adapters and ingestion modules. The connector structure uses a shared core (`connector/shared/`) with vendor-specific adapters (`connector/olex_pi/`, `connector/maxsea_win/`, etc.), while the Core API uses vendor-specific ingestion modules (`ingest_olex`, `ingest_maxsea`, etc.) to convert raw files into normalized data structures.

For detailed information on the multi-plotter connector architecture, see `docs/architecture/multi_plotter_connectors.md`.

