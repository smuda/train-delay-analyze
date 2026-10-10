import argparse
import csv
import http.client
import json
import os
import tempfile
import urllib.error
import urllib.request
from datetime import date, timedelta
from pathlib import Path
from xml.sax.saxutils import escape

API_URL = "https://api.trafikinfo.trafikverket.se/v2/data.json"
KEY_VAR = "TRAFIKVERKET_API_KEY"
TIMEOUT = 30  # seconds
DAYS_BACK = (2, 1)  # only completed trip dates, oldest first

QUOTE = {'"': "&quot;"}

REQUEST = (
    '<REQUEST><LOGIN authenticationkey="{key}"/>'
    '<QUERY objecttype="TrainAnnouncement" schemaversion="1.9"><FILTER>'
    '<EQ name="AdvertisedTrainIdent" value="{train}"/>'
    '<EQ name="ScheduledDepartureDateTime" value="{day}"/>'
    "</FILTER></QUERY></REQUEST>"
)


def trip_dates(today: date, trains_path: Path) -> list:
    """(date, train number or None) for each date to fetch, oldest first."""
    with open(trains_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    result = []
    for days in DAYS_BACK:
        day = (today - timedelta(days=days)).isoformat()
        # ISO dates compare correctly as strings; an empty bound is open
        train = next(
            (
                r["train_number"]
                for r in rows
                if (not r["valid_from"] or r["valid_from"] <= day)
                and (not r["valid_to"] or day <= r["valid_to"])
            ),
            None,
        )
        result.append((day, train))
    return result


def request_day(key: str, train: str, day: str) -> bytes:
    """Raw response body for one trip date; exits with a message on any failure."""
    body = REQUEST.format(
        key=escape(key, QUOTE), train=escape(train, QUOTE), day=day
    ).encode("utf-8")
    req = urllib.request.Request(
        API_URL, data=body, headers={"Content-Type": "text/xml"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as e:
        msg = f"{day}: API request failed: HTTP {e.code}"
        try:
            api_msg = json.loads(e.read())["RESPONSE"]["RESULT"][0]["ERROR"]["MESSAGE"]
            msg += f": {api_msg}".replace(key, "***")
        except Exception:
            pass
        raise SystemExit(msg) from None
    except urllib.error.URLError as e:
        raise SystemExit(f"{day}: API request failed: {e.reason}") from None
    except (OSError, http.client.HTTPException) as e:
        raise SystemExit(f"{day}: API request failed: {e}") from None

    try:
        result = json.loads(raw)["RESPONSE"]["RESULT"][0]
        if "ERROR" in result:
            reason = str(result["ERROR"].get("MESSAGE", "ERROR in result")).replace(key, "***")
        elif not isinstance(result.get("TrainAnnouncement"), list):
            reason = "no TrainAnnouncement list"
        else:
            return raw
    except (ValueError, KeyError, IndexError, TypeError, AttributeError):
        reason = "malformed body"
    raise SystemExit(f"{day}: unexpected API response: {reason}") from None


def write_new(path: Path, data: bytes) -> bool:
    """Write path atomically; False (and nothing written) if it already exists."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        # link, unlike rename, refuses to replace a file another run wrote meanwhile
        os.link(tmp, path)
        return True
    except FileExistsError:
        return False
    finally:
        os.unlink(tmp)


def fetch(raw_dir: Path, trains_path: Path, today: date = None):
    key = os.environ.get(KEY_VAR)
    if not key:
        raise SystemExit(f"{KEY_VAR} is not set")
    raw_dir = Path(raw_dir)
    for day, train in trip_dates(today or date.today(), trains_path):
        path = raw_dir / f"{day}.json"
        if train is None:
            print(f"{day}: no train number")
        elif path.exists():
            print(f"{day}: already present")
        elif write_new(path, request_day(key, train, day)):
            print(f"{day}: written")
        else:
            print(f"{day}: already present")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", default="data/raw", type=Path)
    parser.add_argument("--trains", default="data/trains.csv", type=Path)
    args = parser.parse_args()
    fetch(args.raw, args.trains)
