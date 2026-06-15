# Makefile — Design Spec

**Date:** 2026-06-15
**Status:** Approved

## Overview

A Makefile with two targets to orchestrate the most common developer actions: downloading `signal-cli` into a local `bin/` directory, and running the summarizer agent.

## Targets

### `download-signal-cli`
Downloads `signal-cli` v0.14.5 Linux client tarball from GitHub via `wget`, extracts it into `bin/` (stripping the top-level archive directory), and removes the tarball from `/tmp`.

### `run`
Runs the summarizer agent with `./bin` prepended to `PATH` so the locally installed `signal-cli` is found without a system-wide install.

## File Changes

- **`Makefile`** — new file at repo root with the two targets above and `.PHONY` declarations.
- **`.gitignore`** — append `bin/` to keep extracted binaries out of version control.

## Non-Goals

- Dependency installation (`pip install`)
- DB migration
- Scheduling / cron setup
