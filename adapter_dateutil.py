"""Run only this kit's trusted fixed cases through python-dateutil.

Optional dependency: python-dateutil==2.9.0.post0. No network calls.
The comparator itself does not import or execute this adapter.
"""
from datetime import datetime, timezone
from itertools import islice
from importlib.resources import files
import json
from zoneinfo import ZoneInfo

from dateutil.rrule import rrulestr, rruleset
from boundarykit import load_cases


def expand(case):
    # All local times in v0.1.0 exist and are unambiguous.
    # This deliberately does not assert gap/fold handling by dateutil.
    # Use the installed tzdata package, not an uncontrolled system tz database.
    with files("tzdata.zoneinfo").joinpath(*case["timezone"].split("/")).open("rb") as source:
        zone = ZoneInfo.from_file(source, key=case["timezone"])
    local = lambda value: datetime.fromisoformat(value).replace(tzinfo=zone)
    series = rruleset()
    series.rrule(rrulestr(case["rrule"], dtstart=local(case["dtstart"])))
    for value in case.get("rdates", []):
        series.rdate(local(value))
    for value in case.get("exdates", []):
        series.exdate(local(value))
    values = list(islice(series, 101))
    if len(values) > 100:
        raise ValueError("Fixture expansion exceeded the 100 occurrence limit")
    return [value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") for value in values]


if __name__ == "__main__":
    print(json.dumps({case["id"]: expand(case) for case in load_cases()}, indent=2))
