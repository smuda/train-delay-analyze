import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import report  # noqa: E402

ADV = "2026-10-01T23:34:00.000+02:00"


def ann(activity, loc, canceled=False, adv=ADV, actual=None):
    a = {
        "ActivityType": activity,
        "AdvertisedTrainIdent": "582",
        "LocationSignature": loc,
        "Canceled": canceled,
        "AdvertisedTimeAtLocation": adv,
    }
    if actual:
        a["TimeAtLocation"] = actual
    return a


def arrival(actual, canceled=False):
    return ann("Ankomst", "Uå", canceled=canceled, actual=actual)


def at(minutes_after, seconds=0):
    base = datetime.fromisoformat(ADV)
    return (base + timedelta(minutes=minutes_after, seconds=seconds)).isoformat()


def write_raw(raw_dir, name, announcements):
    raw_dir.mkdir(parents=True, exist_ok=True)
    body = {"RESPONSE": {"RESULT": [{"TrainAnnouncement": announcements}]}}
    (raw_dir / f"{name}.json").write_text(json.dumps(body), encoding="utf-8")


def departure():
    return ann("Avgang", "Cst", adv="2026-10-01T17:21:00.000+02:00",
               actual="2026-10-01T17:22:00.000+02:00")


def write_trip(raw_dir, name, arr):
    write_raw(raw_dir, name, [departure(), arr])


def write_full_set(raw_dir):
    write_trip(raw_dir, "2026-10-01", arrival(at(3)))
    write_trip(raw_dir, "2026-10-02", arrival(at(-4)))
    write_trip(raw_dir, "2026-10-03", arrival(at(15)))
    write_trip(raw_dir, "2026-10-04", arrival(at(29)))
    write_trip(raw_dir, "2026-10-05", arrival(at(200)))
    write_trip(raw_dir, "2026-10-06", arrival(at(10), canceled=True))
    write_raw(raw_dir, "2026-10-07", [departure()])
    write_trip(raw_dir, "2026-10-08", arrival(None))
    write_raw(raw_dir, "2026-10-09", [])


FULL_SUMMARY = (
    "Trips: 8 (2026-10-01 to 2026-10-08). On time: 2/8 (25.0%), "
    "not-arrived trips count as late. Median arrival delay: 15.0 min "
    "over 5 arrived trips. Not arrived: 3."
)


def test_full_set(tmp_path):
    raw, png = tmp_path / "raw", tmp_path / "out" / "r.png"
    write_full_set(raw)
    r = report.report(raw, png)
    assert r["trips"] == 8
    assert r["arrived"] == 5
    assert r["not_arrived"] == 3
    assert r["on_time"] == 2
    assert r["median_delay"] == 15.0
    assert len(r["buckets"]) == 13
    expected = [0] * 13
    expected[0], expected[1], expected[12] = 2, 2, 1
    assert r["buckets"] == expected
    assert r["first_date"] == "2026-10-01"
    assert r["last_date"] == "2026-10-08"
    assert r["summary"] == FULL_SUMMARY
    assert png.exists() and png.stat().st_size > 0


def test_empty_announcements_not_in_date_range(tmp_path):
    raw = tmp_path / "raw"
    write_trip(raw, "2026-10-01", arrival(at(1)))
    write_raw(raw, "2026-10-02", [])
    r = report.report(raw, tmp_path / "r.png")
    assert r["trips"] == 1
    assert r["last_date"] == "2026-10-01"


def test_exactly_six_minutes_not_on_time(tmp_path):
    raw = tmp_path / "raw"
    write_trip(raw, "2026-10-01", arrival(at(6)))
    assert report.report(raw, tmp_path / "r.png")["on_time"] == 0


def test_just_under_six_minutes_on_time(tmp_path):
    raw = tmp_path / "raw"
    write_trip(raw, "2026-10-01", arrival(at(5, 59)))
    # 23:39:59 vs advertised 23:34:00 is 5.98 min
    assert report.report(raw, tmp_path / "r.png")["on_time"] == 1


def test_only_not_arrived(tmp_path):
    raw = tmp_path / "raw"
    write_raw(raw, "2026-10-01", [departure()])
    r = report.report(raw, tmp_path / "r.png")
    assert r["trips"] == 1 and r["arrived"] == 0 and r["not_arrived"] == 1
    assert r["median_delay"] is None
    assert r["buckets"] == [0] * 13
    assert "Median arrival delay: n/a over 0 arrived trips." in r["summary"]


def test_empty_dir_no_trips_no_png(tmp_path):
    raw, png = tmp_path / "raw", tmp_path / "r.png"
    raw.mkdir()
    r = report.report(raw, png)
    assert r["trips"] == 0 and r["arrived"] == 0 and r["not_arrived"] == 0
    assert r["on_time"] == 0
    assert r["median_delay"] is None
    assert r["first_date"] is None and r["last_date"] is None
    assert r["buckets"] == [0] * 13
    assert r["summary"] == f"No trips in {raw}."
    assert not png.exists()


def test_cli(tmp_path):
    raw, png = tmp_path / "raw", tmp_path / "cli.png"
    write_full_set(raw)
    env = {"MPLCONFIGDIR": str(tmp_path), "PATH": "/usr/bin:/bin"}
    p = subprocess.run(
        [sys.executable, str(ROOT / "report.py"), "--raw", str(raw), "--out", str(png)],
        capture_output=True, text=True, env=env, cwd=tmp_path,
    )
    assert p.returncode == 0, p.stderr
    assert FULL_SUMMARY in p.stdout
    assert png.exists() and png.stat().st_size > 0
