# capaldi

[![Build Status](https://travis-ci.org/moscowpython/capaldi.svg?branch=master)](https://travis-ci.org/moscowpython/capaldi)

Bot for learn.python.ru students&staff.

## Installation

```terminal
pip install git+https://github.com/moscowpython/capaldi.git
```

## Usage

First, provide following env vars:

- Telegram bot token (`TELEGRAM_BOT_TOKEN`).
- Telegram bot proxy settings (`TELEGRAM_PROXY_URL`, `TELEGRAM_PROXY_LOGIN`,
  `TELEGRAM_PROXY_PASSWORD`).
- Telegram admin username (with @, like `@melevir`, `TELEGRAM_ADMIN_USERNAME`).
  Optional.
- Airtable credentials (`AIRTABLE_API_KEY` and `AIRTABLE_BASE_ID`).
- Sentry API url (`SENTRY_URL`).
- Redis url (in format `redis://[[username]:[password]]@localhost:6379/0`, `REDIS_URL`).

Then run one of following commands:

- `lp_run_bot` – run Telegram bot.
- `lp_ask_for_feedback` – ask students for feedback on current week.
- `lp_send_stat_report` – send feedback statistics of current week.
- `lp_notify_on_tomorrow_event` – notify students if there is course event tomorrow.

Run any command with `--help` to gel params list.
