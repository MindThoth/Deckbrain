# Database Migrations (Alembic)

This document explains the database migration system used in DeckBrain Core API.

## What are Alembic Migrations?

Alembic is a database migration tool for SQLAlchemy. Migration files in `core-api/alembic/versions/` track all changes to the database schema over time.

## Migration Files

All migration files are stored in: `core-api/alembic/versions/`

### Current Migrations

1. **`001_create_devices_heartbeats_file_records.py`**
   - Creates initial tables: `devices`, `heartbeats`, `file_records`
   - Base schema for device registration and file tracking

2. **`272465ebd1ab_add_sha256_and_received_at_to_file_.py`**
   - Adds `sha256` hash column to `file_records` for deduplication
   - Adds `received_at` timestamp to `file_records`

3. **`003_add_trips_tows_soundings_tables.py`**
   - Creates `trips`, `tows`, and `soundings` tables
   - Adds relationships and indexes for trip data

## Why These Files Exist

- **Version Control**: Track database schema changes in git
- **Reproducibility**: Apply same schema changes to dev, staging, production
- **Rollback**: Can downgrade schema if needed
- **Team Collaboration**: Everyone gets the same database structure

## How Migrations Work

1. **Create Migration**: After changing models, run:
   ```bash
   alembic revision --autogenerate -m "description"
   ```

2. **Apply Migrations**: Run all pending migrations:
   ```bash
   alembic upgrade head
   ```

3. **Rollback**: Undo last migration:
   ```bash
   alembic downgrade -1
   ```

## File Organization

```
core-api/
  alembic/
    versions/          ← Migration files go here (correct location)
      001_*.py
      003_*.py
      ...
    env.py             ← Alembic configuration
    script.py.mako     ← Migration template
  alembic.ini          ← Alembic settings
```

**This is the standard Alembic structure and should NOT be changed.**

## Important Notes

- ✅ Migration files should be committed to git
- ✅ Never edit existing migrations (create new ones instead)
- ✅ Migration filenames include revision IDs for tracking
- ✅ Always test migrations before applying to production

