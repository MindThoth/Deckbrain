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
## 3. Versioning, Branches, and Logs

DeckBrain uses a simple but strict structure for branches and logs so that humans and AI models can collaborate without making a mess.

### Branches

- main
  - Always in a stable, releasable state.
  - Only merged into when a feature is complete.
  - Tagged with semantic versions like v0.1.0, v0.2.0, etc.

- feature/<name>
  - Used for active development of a specific feature.
  - Examples:
    - feature/trips-v0.2
    - feature/tow-notes
    - feature/history-tab
  - All work for that feature happens here until it's ready to merge into main.

(We may add hotfix/<name> branches later for urgent fixes.)

### DEVLOG vs CHANGELOG

- DEVLOG.md
  - Detailed, chronological development log.
  - Every work session (human or AI) should append an entry.
  - Each entry should include:
    - Date
    - Target version tag with "-dev" (for example v0.2.0-dev)
    - Branch name (for example feature/trips-v0.2)
    - Model or developer name (for example GPT-4o, Claude 3.5, Cursor)
    - Short summary of what changed

  Example DEVLOG entry (do NOT add this example to the file, just keep it as guidance):

    ### 2025-12-11 – v0.2.0-dev – branch: feature/trips-v0.2
    - Model: GPT-4o via Cursor
    - Changes:
      - Added stub trips endpoints to core-api.
      - Created Trips page in dashboard with sidebar and map placeholder.

- CHANGELOG.md
  - High-level, release-oriented log for the main branch.
  - Updated only when a feature branch is merged into main and we consider that a new version.
  - Uses semantic versioning: 0.1.0, 0.2.0, 0.3.0, etc.

  Example CHANGELOG entry (again, guidance only):

    ## [0.2.0] – 2025-12-11
    ### Added
    - Initial Trips vertical slice:
      - Basic trip list and track endpoints in core-api.
      - Trips tab in dashboard with map and sidebar.

### Typical Workflow

1. Create a feature branch from main:
   - git checkout main && git pull
   - git checkout -b feature/trips-v0.2

2. Do work on the feature branch.
   - Update code and docs.
   - Append an entry to DEVLOG.md with a "-dev" version tag and branch name.
   - Commit and push.

3. When the feature is ready:
   - Merge feature/... into main.
   - Add a new entry to CHANGELOG.md with the final version (for example 0.2.0).
   - Optionally create a git tag: git tag v0.2.0.

This keeps:
- DEVLOG.md as the full detailed history, and
- CHANGELOG.md as the clean, user-facing release history for the main branch.

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
