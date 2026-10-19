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
  GitHub starts scheduled runs late, so far between 07:30 and 10:10
  UTC; a run not there by morning has usually not been skipped. The
  margin before trips start to disappear from the API is smaller
  than the schedule suggests.
- `report.py` reads the raw archive offline, writes `report.png`
  and prints a summary line. The chart shows an on-time bar (under
  6 minutes late), a 6 to 15 minute bar, then 15-minute buckets up
  to the latest arrival, plus a not-arrived bar.
  It also prints the delay gained on each stretch between advertised
  stops, and while standing at each stop, averaged over all trips.

The service's train numbers and their valid date ranges are in
`data/trains.csv`, edited by hand.
Station names for Trafikverket's location codes are in
`data/stations.csv`, also edited by hand.
The names come from Trafikverket's TrainStation data
(`AdvertisedLocationName` by `LocationSignature`). Query it with
schema version 1.4, since 1.5 rejects `LocationSignature`; fetching
the whole list without a filter works. When a report shows a code
instead of a name, add that row.

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
