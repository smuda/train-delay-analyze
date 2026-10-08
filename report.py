import argparse
import json
import statistics
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

DESTINATION = "Uå"  # Umeå C location signature
BUCKET_WIDTH = 15  # minutes
LAST_EDGE = 180  # last bucket is >= LAST_EDGE
ON_TIME_LIMIT = 6  # RT+5: on time if delay < 6 min

N_BUCKETS = LAST_EDGE // BUCKET_WIDTH + 1


def arrival_delay(announcements):
    """Arrival delay in minutes at DESTINATION, or None if the train did not arrive."""
    for a in announcements:
        if a.get("ActivityType") == "Ankomst" and a.get("LocationSignature") == DESTINATION:
            if a.get("Canceled") or "TimeAtLocation" not in a:
                return None
            advertised = datetime.fromisoformat(a["AdvertisedTimeAtLocation"])
            actual = datetime.fromisoformat(a["TimeAtLocation"])
            return (actual - advertised).total_seconds() / 60
    return None


def report(raw_dir: Path, png_path: Path) -> dict:
    raw_dir = Path(raw_dir)
    buckets = [0] * N_BUCKETS
    delays = []
    dates = []
    not_arrived = 0
    on_time = 0

    for path in sorted(raw_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        announcements = data["RESPONSE"]["RESULT"][0]["TrainAnnouncement"]
        if not announcements:
            continue
        dates.append(path.stem)
        delay = arrival_delay(announcements)
        if delay is None:
            not_arrived += 1
            continue
        delays.append(delay)
        buckets[min(int(max(delay, 0) // BUCKET_WIDTH), LAST_EDGE // BUCKET_WIDTH)] += 1
        if delay < ON_TIME_LIMIT:
            on_time += 1

    arrived = len(delays)
    trips = arrived + not_arrived
    median = statistics.median(delays) if delays else None
    first_date = dates[0] if dates else None
    last_date = dates[-1] if dates else None

    if trips == 0:
        summary = f"No trips in {raw_dir}."
    else:
        median_part = (
            f"{median:.1f} min over {arrived} arrived trips"
            if arrived
            else "n/a over 0 arrived trips"
        )
        summary = (
            f"Trips: {trips} ({first_date} to {last_date}). "
            f"On time: {on_time}/{trips} ({100 * on_time / trips:.1f}%), "
            f"not-arrived trips count as late. "
            f"Median arrival delay: {median_part}. "
            f"Not arrived: {not_arrived}."
        )
        _plot(buckets, not_arrived, first_date, last_date, Path(png_path))

    return {
        "trips": trips,
        "arrived": arrived,
        "not_arrived": not_arrived,
        "on_time": on_time,
        "median_delay": median,
        "buckets": buckets,
        "first_date": first_date,
        "last_date": last_date,
        "summary": summary,
    }


def _plot(buckets, not_arrived, first_date, last_date, png_path):
    labels = [
        f"{i * BUCKET_WIDTH}–{(i + 1) * BUCKET_WIDTH}" for i in range(N_BUCKETS - 1)
    ] + [f"≥{LAST_EDGE}"]
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar(range(N_BUCKETS), buckets, color="tab:blue")
    # gap of one slot keeps the not-arrived bar visually separate
    ax.bar(N_BUCKETS + 1, not_arrived, color="tab:red")
    ax.set_xticks(list(range(N_BUCKETS)) + [N_BUCKETS + 1])
    ax.set_xticklabels(labels + ["Not arrived"], rotation=45, ha="right")
    ax.set_xlabel("Arrival delay at Umeå C (min)")
    ax.set_ylabel("Trips")
    ax.set_title(f"Train arrival delays, {first_date} to {last_date}")
    fig.tight_layout()
    png_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(png_path)
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", default="data/raw", type=Path)
    parser.add_argument("--out", default="report.png", type=Path)
    args = parser.parse_args()
    print(report(args.raw, args.out)["summary"])
