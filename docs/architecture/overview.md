# DeckBrain Architecture Overview

This overview defers to `DECKBRAIN_FOUNDATION.md` for the full system description. Use this file to capture diagrams and deeper architecture details as they evolve.

## Multi-Plotter Support

DeckBrain is designed as a multi-plotter platform, supporting Olex, MaxSea TimeZero, and other navigation systems. This document currently focuses on Olex as the initial integration. MaxSea and other plotters will follow the same connector → Core API pattern. For detailed information on how different plotters integrate, see `docs/architecture/multi_plotter_connectors.md`.

