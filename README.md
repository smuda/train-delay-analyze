# train-delay-analyze

Measures how late SJ's Stockholm C 17:21 to Umeå C 23:34 service
arrives at Umeå C, as a histogram of arrival delay over many days.
Data comes from Trafikverket's open API (CC0). Terms such as arrival
delay, not arrived and on time are defined in `CONTEXT.md`.

## How it works

- `fetch.py` downloads every announcement for the service's train
  number for the last two completed trip dates and stores each
  response unmodified as `data/raw/YYYY-MM-DD.json`. Stored files
  are never overwritten.
- A GitHub Actions workflow (`.github/workflows/fetch.yml`) runs
  `fetch.py` daily at 03:00 UTC and commits new raw files to `main`.
  The API keeps data for only about 3 days, so a trip not fetched in
  time is lost for good.
- `report.py` reads the raw archive offline, writes `report.png`
  (arrival delay in 15-minute buckets plus a not-arrived bar) and
  prints a summary line.

The service's train numbers and their valid date ranges are in
`data/trains.csv`, edited by hand.

## Setup

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

The workflow reads the API key from the `TRAFIKVERKET_API_KEY`
repository secret. To run `fetch.py` locally, put the key in `.env`
(ignored by git):

```sh
TRAFIKVERKET_API_KEY=...
```

## Usage

```sh
./runme.sh
```

pulls the latest raw files and runs the report. To fetch by hand, for
example after a skipped scheduled run:

```sh
set -a; . ./.env; set +a
.venv/bin/python fetch.py
```

## Tests

```sh
.venv/bin/python -m pytest tests
```
