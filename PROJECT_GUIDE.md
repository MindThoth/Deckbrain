# DeckBrain Project Guide
This guide explains how to work inside the DeckBrain repository. Read it before contributing.

- For the full vision, architecture, module layout, and roadmap, see `DECKBRAIN_FOUNDATION.md`.
- For day-to-day history, check the latest entries in `DEVLOG.md`.

----------------------------------------------------
## 1. How the repo is organized (core + modules, concise)

- Each system uses a stable `core/` plus feature-specific modules.
  - Connector: `connector/core/`, `connector/modules/<feature>/`
  - Core API: `core-api/core/`, `core-api/modules/<feature>/`
  - Dashboard: `dashboard/core/`, `dashboard/features/<feature>/`
- Modules may import from `core/` but not from each other.
- Adding a feature means adding or extending a module, not coupling unrelated ones.

----------------------------------------------------
## 2. Working rules for humans and AI

1. Read `DECKBRAIN_FOUNDATION.md` (context) and this guide (workflow).
2. Check `DEVLOG.md` to understand recent changes.
3. Follow module boundaries; keep cross-cutting helpers in `core/`.
4. After changes, append a DEVLOG entry (date, version tag, model, summary).
5. Keep code style consistent with existing files.

----------------------------------------------------
## 3. Branching workflow

- `main` → stable
- `dev` → active work
- `feature/<name>` → new modules/features
- `fix/<name>` → bug fixes

----------------------------------------------------
## 4. Commit message style

Examples:
- `feat: add trips module skeleton`
- `fix: heartbeat queue bug`
- `docs: update architecture guide`

----------------------------------------------------
## 5. Before making ANY change

An AI model MUST:
1. Read `DECKBRAIN_FOUNDATION.md` and this `PROJECT_GUIDE.md`.
2. Read latest entries in `DEVLOG.md`.
3. Respect core + modules boundaries.
4. Document its changes in `DEVLOG.md`.

----------------------------------------------------
End of project guide.
