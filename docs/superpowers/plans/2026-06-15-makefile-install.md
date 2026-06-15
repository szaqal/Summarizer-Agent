# Makefile `install` Target Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an `install` target to the Makefile that creates a `.venv` virtual environment and installs `requirements.txt` into it, and update `run` to use `.venv/bin/python` directly.

**Architecture:** Single-file change to `Makefile` — add `install` to `.PHONY`, insert the `install` target, and replace `python` with `.venv/bin/python` in the `run` target. No other files need touching (`.venv/` is already gitignored).

**Tech Stack:** GNU Make, Python venv, pip

---

### Task 1: Update `Makefile`

**Files:**
- Modify: `Makefile`

- [ ] **Step 1: Replace the Makefile with the updated version**

```makefile
.PHONY: download-signal-cli install run

SIGNAL_CLI_VERSION = 0.14.5
SIGNAL_CLI_URL     = https://github.com/AsamK/signal-cli/releases/download/v$(SIGNAL_CLI_VERSION)/signal-cli-$(SIGNAL_CLI_VERSION)-Linux-client.tar.gz

download-signal-cli:
	mkdir -p bin
	wget -O /tmp/signal-cli.tar.gz $(SIGNAL_CLI_URL)
	tar -xzf /tmp/signal-cli.tar.gz -C bin --strip-components=1
	rm /tmp/signal-cli.tar.gz

install:
	python -m venv .venv
	.venv/bin/pip install -r requirements.txt

run:
	PATH=./bin:$$PATH .venv/bin/python -m summarizer_agent.main
```

> **Note:** Every recipe line must be indented with a real tab character. Verify with `cat -A Makefile` — recipe lines must show `^I` at the start.

- [ ] **Step 2: Verify tab indentation**

```bash
cat -A Makefile | grep "^	"
```

Expected: all recipe lines (`mkdir`, `wget`, `tar`, `rm`, `python -m venv`, `.venv/bin/pip`, `PATH=`) start with `^I`.

- [ ] **Step 3: Smoke-test `make install`**

```bash
make install
```

Expected output (abbreviated):
```
python -m venv .venv
.venv/bin/pip install -r requirements.txt
Collecting langchain
...
Successfully installed langchain ...
```

Then verify the venv exists and contains the packages:

```bash
.venv/bin/pip list | grep -E "langchain|psycopg2|requests|beautifulsoup4"
```

Expected: all four packages appear in the list.

- [ ] **Step 4: Verify `make install` is idempotent**

```bash
make install
```

Running a second time should succeed without error. `python -m venv .venv` on an existing venv completes silently; pip re-installs or confirms packages are already up to date.

- [ ] **Step 5: Smoke-test `make run` uses the venv**

Without a configured `.env`, the `run` target will fail on a missing env var — that's expected and confirms the venv's Python is being used (not the system one):

```bash
make run 2>&1 | head -5
```

Expected: output contains `KeyError` for a missing env var (e.g., `DATABASE_URL`), not `python: command not found` or `ModuleNotFoundError: No module named 'summarizer_agent'`.

- [ ] **Step 6: Commit**

```bash
git add Makefile
git commit -m "chore: add install target and use venv python in run"
```
