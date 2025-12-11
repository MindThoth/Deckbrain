# Testing Strategy (Draft)

Testing will be organized per service, with tests living under `tests/` in `connector/`, `core-api/`, and `dashboard/`.

- Unit tests: core logic in each service (parsers, utilities, data mappers).
- Integration tests: Core API endpoints and data flows between components.
- End-to-end tests (future): Dashboard flows and cross-service interactions once the stack is runnable.

Open questions / TODO:
- Decide test frameworks per service (e.g., pytest for Python, jest/playwright for Next.js).
- Define fixture data for Olex sample files and API responses.
- Add CI hooks once tests exist.

