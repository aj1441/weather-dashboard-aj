# Code Simplification Ideas

This document collects observations and suggestions for simplifying the project. The goal is to make the code base easier to understand and maintain.

## 1. Consolidate utility modules
- Several files inside `core/` offer overlapping helper functions. Grouping common utilities (string formatting, database helpers, etc.) into a single module will reduce cross imports.

## 2. Limit module size
- Some modules exceed a few hundred lines (e.g. `core/api.py`). Splitting these into focused submodules (`api_client.py`, `forecast_processing.py`) will make navigation simpler.

## 3. Reduce global state
- A few functions rely on module-level variables. Encapsulate related state in classes or pass values explicitly to improve testability.

## 4. Embrace type hints
- Many functions already use basic hints, but expanding coverage (especially return types) will help static analysis tools detect bugs early.

## 5. Remove legacy fallbacks
- The repository retains older helper functions and placeholder implementations. After confirming no remaining dependencies, removing these blocks will clarify the modern code paths.

For a larger refactor, consider adopting a lightweight framework (such as `typer` for CLI utilities) or structuring the GUI with a model-view-controller approach.
