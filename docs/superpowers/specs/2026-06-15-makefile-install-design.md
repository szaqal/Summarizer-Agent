# Makefile `install` Target — Design Spec

**Date:** 2026-06-15
**Status:** Approved

## Overview

Add an `install` target to the existing Makefile that creates a Python virtual environment and installs dependencies from `requirements.txt`. Update the `run` target to use the venv's Python directly so no manual activation is required.

## Changes

### `Makefile`

- Add `install` to `.PHONY`.
- New `install` target:
  - `python -m venv .venv` — creates `.venv/` in the project root (idempotent: won't overwrite an existing venv).
  - `.venv/bin/pip install -r requirements.txt` — installs all dependencies into the venv.
- Update `run` target: replace `python` with `.venv/bin/python` so `make run` works without manual `source .venv/bin/activate`.

### `.gitignore`

`.venv/` is already present in `.gitignore` from a previous session — no change needed.

## Workflow

```
make install            # first-time setup: creates venv, installs deps
make download-signal-cli  # download signal-cli binary into bin/
make run                # run the agent (no activation needed)
```

## Non-Goals

- Pinning dependency versions (handled separately if needed)
- Combined `setup` target merging install + download
