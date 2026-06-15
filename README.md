# Summarizer Agent

Fetches unsummarized articles from a PostgreSQL database, generates Polish-language summaries using the Mistral API via LangChain, and delivers a digest via Signal messenger.

## Setup

### 1. Install Python dependencies

```bash
make install
```

### 2. Configure environment

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

```
DATABASE_URL=postgresql://user:password@host/dbname
MISTRAL_API_KEY=your-mistral-api-key
SIGNAL_SENDER=+48123456789   # phone number signal-cli will send from
SIGNAL_RECIPIENT=+48987654321 # phone number to receive the digest
```

### 3. Download signal-cli

```bash
make download-signal-cli
```

Requires Java 25. If using SDKMAN:

```bash
sdk install java 25.0.2-open
```

### 4. Register signal-cli with Signal

signal-cli can be set up in two ways. **Linking (recommended)** adds it as a secondary device tied to your existing Signal account, so your phone app keeps working. **Registering** creates a new primary device for a separate phone number.

#### Option A — Link to existing account (recommended)

Have your phone ready with Signal open, then:

```bash
make link
```

signal-cli prints a `sgnl://linkdevice?...` URI. Immediately on your phone:

- Settings → Linked Devices → Link New Device → scan the QR code

To show the QR code directly in the terminal (requires `qrencode`):

```bash
sudo apt install qrencode
make link 2>&1 | grep sgnl:// | qrencode -t ansiutf8
```

`SIGNAL_SENDER` in `.env` should be set to the phone number of the Signal account you linked to.

#### Option B — Register a new number

Use a dedicated phone number that is not already registered with Signal on any device.

**Step 1 — Get a captcha token:**

1. Open https://signalcaptchas.org/registration/generate.html in a browser
2. Solve the captcha
3. Right-click the **"Open Signal"** link → Copy link address
4. The copied link starts with `signalcaptcha://...`

**Step 2 — Register:**

```bash
make register CAPTCHA='signalcaptcha://...'
```

Signal sends an SMS with a 6-digit verification code to `SIGNAL_SENDER`.

**Step 3 — Verify:**

```bash
make verify CODE=123456
```

## Running

```bash
make run
```

Processes up to 50 unsummarized articles per run, writes summaries back to the database, and sends a single Signal digest to `SIGNAL_RECIPIENT`.

## Database migration

Run once to add the `summary` and `summarized_at` columns to `rss_items`:

```bash
psql "$DATABASE_URL" -f db_migration.sql
```


Deliver message `./signal-cli -a  SENDER send -m message RECIPIENT`
