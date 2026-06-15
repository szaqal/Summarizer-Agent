# signal-cli Registration Targets — Design Spec

**Date:** 2026-06-15
**Status:** Approved

## Overview

Add two Makefile targets to register and verify a phone number with signal-cli, reading `SIGNAL_SENDER` from the existing `.env` file.

## Targets

### `register`
Sources `.env` to load `SIGNAL_SENDER`, then calls:
```
./bin/signal-cli -a $SIGNAL_SENDER register
```
Triggers an SMS verification code to the `SIGNAL_SENDER` phone number.

### `verify`
Requires `CODE` to be passed on the command line (`make verify CODE=123456`). Guards against missing `CODE` with a usage error, then calls:
```
./bin/signal-cli -a $SIGNAL_SENDER verify <CODE>
```

## Implementation

```makefile
register:
	source .env && ./bin/signal-cli -a $$SIGNAL_SENDER register

verify:
	@test -n "$(CODE)" || (echo "Usage: make verify CODE=<verification-code>" && exit 1)
	source .env && ./bin/signal-cli -a $$SIGNAL_SENDER verify $(CODE)
```

Both targets added to `.PHONY`. `source .env` works because `SHELL := /bin/bash` is already set. `$$SIGNAL_SENDER` double-escapes Make's `$` expansion so the shell sees `$SIGNAL_SENDER` after sourcing `.env`. `$(CODE)` is a Make variable passed directly on the command line.

## Usage

```bash
make register           # triggers SMS to SIGNAL_SENDER
make verify CODE=123456 # submits the received code
```

## Non-Goals

- Voice call registration (`--voice` flag)
- Captcha handling
- Link device (secondary device registration)
