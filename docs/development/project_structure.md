# DeckBrain Project Structure

This document explains the organization of the DeckBrain repository and why files are located where they are.

## Repository Layout

```
DeckBrain/
├── connector/          # Vessel-side connector agents
│   ├── shared/         # Shared core for all connectors
│   ├── olex_pi/        # Olex Raspberry Pi connector
│   └── maxsea_win/     # MaxSea Windows connector
├── core-api/           # FastAPI backend service
│   ├── core/           # Core utilities and models
│   ├── modules/        # Feature modules
│   ├── alembic/        # Database migrations
│   └── scripts/        # Utility scripts
├── dashboard/          # Next.js web dashboard (future)
├── docs/               # Documentation
│   ├── architecture/   # Architecture documentation
│   ├── development/    # Development guides
│   └── product/        # Product documentation
└── [root docs]         # Core project docs (README, DEVLOG, etc.)
```

## Why This Structure?

### Connector Directory

**`connector/README.md`**: Overview of multi-connector architecture
- Explains shared core + vendor adapters pattern
- Documents common protocol

**`connector/shared/README.md`**: Details about shared core
- Specific to shared functionality
- Used by all vendor connectors

**`connector/olex_pi/README.md`**: Olex-specific connector
- Platform: Raspberry Pi/Linux
- Vendor-specific details

**`connector/maxsea_win/README.md`**: MaxSea-specific connector
- Platform: Windows
- Vendor-specific details

**Why multiple READMEs?**
- Each directory has its own README for clarity
- Root README provides overview
- Subdirectory READMEs provide details
- This is standard practice for modular projects

### Core API Directory

**`core-api/alembic/versions/`**: Database migration files
- **001_*.py**: Initial schema (devices, heartbeats, file_records)
- **272465ebd1ab_*.py**: Added sha256 and received_at
- **003_*.py**: Added trips, tows, soundings tables

**Why are these files here?**
- This is the **standard Alembic location** for migrations
- Alembic requires migrations in `alembic/versions/`
- Migration files track database schema changes over time
- They should be committed to git for version control

**See**: `docs/development/database_migrations.md` for details

### Documentation Directory

**`docs/architecture/`**: System architecture docs
- Multi-plotter connectors
- Module system
- Data flow

**`docs/development/`**: Development guides
- Database migrations
- Environment setup
- Testing strategy

**`docs/product/`**: Product documentation
- Feature roadmap
- User guides (future)

## File Organization Principles

1. **Core + Modules Pattern**: Each system (connector, core-api, dashboard) uses core + modules
2. **Vendor-Agnostic Core**: Shared code in `shared/` or `core/`
3. **Vendor-Specific Modules**: Vendor code in `olex_pi/`, `maxsea_win/`, etc.
4. **Standard Locations**: Use standard tool locations (e.g., Alembic migrations)
5. **Documentation Co-location**: READMEs in each directory explain that directory

## What NOT to Change

- ✅ **Alembic migrations location**: Must stay in `alembic/versions/`
- ✅ **Module structure**: Core + modules pattern is intentional
- ✅ **README files**: Multiple READMEs are intentional for clarity

## Questions?

If you see a file and wonder why it's there:
1. Check the directory's README.md
2. Check `DECKBRAIN_FOUNDATION.md` for architecture decisions
3. Check `docs/development/` for development-specific explanations

