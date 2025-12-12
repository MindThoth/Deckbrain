# Commit, DEVLOG, and CHANGELOG Guidelines

This document explains how DeckBrain uses git commits, DEVLOG entries, and CHANGELOG entries to maintain a clear, professional development history. All contributors (human and AI) should follow these guidelines.

## 1. Git Commits — "The Technical History"

- Every push creates a commit.
- Commits should be small, atomic, and descriptive.
- Use a short Conventional Commit prefix when possible:
  - `feat:` (new functionality)
  - `docs:` (documentation changes)
  - `chore:` (cleanup, moves, structure)
  - `fix:` (bug fixes)
  - `refactor:` (internals changed)
- Commits DO NOT need to match DEVLOG entries one-to-one.
- A single DEVLOG entry may cover multiple commits.
- Keep commit messages concise; detailed explanations belong in DEVLOG.

**Examples:**
- `feat: add trips module skeleton`
- `docs: expand core-api README with full service documentation`
- `chore: reorganize repo docs and service folders`
- `fix: heartbeat queue bug`

## 2. DEVLOG — "The Engineering Journal"

The DEVLOG documents meaningful units of work and serves as the engineering journal for the project.

### When to Update DEVLOG

**Required for:**
- Major updates to architecture
- Documentation improvements (when substantial)
- Feature development
- Refactors that change behavior
- Multi-file changes
- Any real work that affects the codebase structure or functionality

**NOT required for:**
- Typos
- Formatting-only changes
- Tiny doc edits (single sentence fixes)
- File moves with no semantic change
- Minor whitespace adjustments

### DEVLOG Entry Structure

Each DEVLOG entry should include:

- **Date**: YYYY-MM-DD format
- **Version**: Dev version tag (e.g., v0.1.4-dev)
- **Branch**: Branch name where work was done (e.g., main, feature/trips-v0.2)
- **Model**: AI model or developer name (e.g., Cursor, Claude 3.5, GPT-4o)
- **Changes**: Summary of meaningful work performed
- **Notes**: Optional additional context

**Example:**
```
### 2025-12-11 – v0.1.4-dev – branch: main
- Model: Cursor (with GPT-based assistant)
- Changes:
  - Expanded core-api/README.md into a full service README describing responsibilities, structure, and links to API/schema docs.
- Notes:
  - This makes the Core API easier to understand in isolation and clarifies where to find API and database documentation.
```

### DEVLOG Versioning

- Use dev versions: `vX.Y.Z-dev`
- Increment appropriately based on scope:
  - Patch increment (v0.1.X-dev) for small changes, docs, refactors
  - Minor increment (v0.X.0-dev) for new features or significant changes
  - Major increment (vX.0.0-dev) for breaking changes or major architectural shifts
- Only DEVLOG entries update dev versions.

## 3. CHANGELOG — "Public Release Notes"

The CHANGELOG is the public-facing release history for the main branch.

### When to Update CHANGELOG

**ONLY update CHANGELOG for:**
- Official versions or public releases
- When merging a stable feature branch into main
- When creating a new release version (e.g., v0.2.0)

**Do NOT update CHANGELOG for:**
- Documentation work
- Dev scaffolding
- Internal architecture changes
- Experimental branches
- Work-in-progress features
- DEVLOG-only updates

### CHANGELOG Entry Structure

CHANGELOG entries use semantic versioning without the `-dev` suffix:

```
## [0.2.0] – 2025-12-11
### Added
- Initial Trips vertical slice:
  - Basic trip list and track endpoints in core-api.
  - Trips tab in dashboard with map and sidebar.
```

## 4. Branching Rules (Summarized)

- **main**: Stable, versioned releases. Only merge complete, tested features.
- **feature/<name>**: Active development branches for new features or major changes.
- **hotfix/<name>**: Bug fixes applied directly to main (for urgent issues).
- **Never push experimental or untested changes directly to main.**

For detailed branching workflow, see `PROJECT_GUIDE.md` section 3.

## 5. Versioning Rules (Summarized)

- **Dev versions**: `vX.Y.Z-dev` (used in DEVLOG)
- **Production versions**: `vX.Y.Z` (used in CHANGELOG and git tags)
- Only DEVLOG entries update dev versions.
- Production versions update CHANGELOG when merging to main.

## 6. Relationship Summary

The three layers work together:

- **Commits** = Technical diff (what changed in code)
- **DEVLOG** = Human-readable engineering reasoning (why and how work was done)
- **CHANGELOG** = Public-facing release history (what users need to know)

**Flow:**
- Commits feed into DEVLOG (multiple commits may be summarized in one DEVLOG entry)
- DEVLOG feeds into CHANGELOG (when features are complete and merged to main)

## 7. Expectations for AIs and Collaborators

### For AI Models

- **Do NOT update CHANGELOG** unless specifically instructed to do so.
- **Do update DEVLOG** when making meaningful progress (architecture, features, substantial docs).
- Keep commit titles short and descriptive; DEVLOG entries long and clear.
- Follow `PROJECT_GUIDE.md` and `DECKBRAIN_FOUNDATION.md` for structure and conventions.
- When in doubt, err on the side of documenting in DEVLOG rather than skipping it.

### For Human Contributors

- Follow the same guidelines as AI models.
- Use DEVLOG to explain your reasoning and approach.
- Update CHANGELOG only when preparing a release.
- Keep commits atomic and well-described.

## 8. Quick Reference

| Action | Update Commit? | Update DEVLOG? | Update CHANGELOG? |
|--------|---------------|----------------|-------------------|
| Fix typo | ✅ | ❌ | ❌ |
| Add new feature | ✅ | ✅ | ❌ (until release) |
| Refactor code | ✅ | ✅ | ❌ |
| Update architecture docs | ✅ | ✅ | ❌ |
| Merge feature to main | ✅ | ✅ | ✅ (if releasing) |
| Release new version | ✅ | ✅ | ✅ |

## 9. Best Practices

1. **Commit often, DEVLOG meaningfully**: Make small, frequent commits, but group related work in DEVLOG entries.
2. **Be descriptive**: DEVLOG entries should explain the "why" and "how", not just the "what".
3. **Link related work**: Reference related DEVLOG entries or issues when relevant.
4. **Keep CHANGELOG clean**: Only include user-facing changes and completed features.
5. **Version consistently**: Follow semantic versioning principles for both dev and production versions.

---

For more details on branching and workflow, see `PROJECT_GUIDE.md`.  
For the overall project vision and architecture, see `DECKBRAIN_FOUNDATION.md`.

