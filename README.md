# RRULE Boundary Kit 0.1.0

**12 recurrence fixtures + an offline Python comparator. Free, MIT licensed.**

Does “monthly on the 31st” become February 28 in your application? Does a
Sunday 09:00 meeting move after daylight saving time changes? Use a small,
fixed set of inputs and expected UTC occurrences to check your integration.

[Download ZIP](https://github.com/taroyamada3173-sys/rrule-boundary-kit/archive/refs/heads/main.zip) ·
[Report a result](https://github.com/taroyamada3173-sys/rrule-boundary-kit/issues/new?template=feedback.md)

## Use it with your implementation

Python 3.10 or later is needed for the comparator. It uses only the standard
library. Download and extract the ZIP, then run from its directory:

```sh
python boundarykit.py list
```

Read `cases.json`. For each case, expand `rrule` from `dtstart` in the named
IANA `timezone`, combine any `rdates`, then apply `exdates`. The local inputs
are ISO timestamps without offsets; their timezone is explicit. Every rule
is finite and DTSTART matches the rule. Return each final occurrence once,
in chronological order, normalized to UTC seconds:

```json
{
  "month_31_skip": [
    "2026-01-31T09:00:00Z",
    "2026-03-31T09:00:00Z",
    "2026-05-31T09:00:00Z",
    "2026-07-31T09:00:00Z",
    "2026-08-31T09:00:00Z"
  ]
}
```

Include **all 12 case IDs** in your output file. The snippet above is only
one case. Use `python boundarykit.py example` to see the complete output
format. That command prints the fixed expectations; checking its output is
only a format demonstration, not a test of your recurrence engine.

```sh
python boundarykit.py check actual.json
```

Exit codes: `0` = all cases match, `1` = differences or missing/unknown cases,
`2` = invalid input. JSON output lists missing/extra occurrences and ordering
differences. Duplicate occurrences and duplicate JSON keys are not silently
discarded. A mismatch may be an adapter or normalization issue, not an engine
bug. Passing these fixtures is not full RFC conformance.

## Try the included dateutil adapter

The optional adapter demonstrates a real recurrence-library run:

```sh
python -m pip install -r requirements-demo.txt
python adapter_dateutil.py > actual.json
python boundarykit.py check actual.json
python -m unittest -v test_boundarykit.py
```

Use an isolated Python environment for optional dependencies. The adapter
only expands this kit's fixed cases, with a 100-occurrence limit. There is no
network access at runtime and no calendar upload or account requirement.

## Coverage and limits

| Cases | What to inspect |
| --- | --- |
| Monthly 31st / last calendar day | Skipping versus end-of-month selection |
| February 29 | Leap-year gaps |
| Last weekday / second Monday | BYSETPOS and ordinal BYDAY |
| UNTIL | Exact inclusive endpoint |
| EXDATE / RDATE | No COUNT refill, duplicate collapse, exclusion precedence |
| WKST Monday / Sunday | Fortnightly week-boundary differences |
| New York spring / autumn | Local 09:00 preservation with different UTC offsets |

This version excludes nonexistent or ambiguous local times, all-day events,
VTIMEZONE parsing, RECURRENCE-ID overrides, unbounded rules and full ICS file
validation. It checks occurrence starts, not event durations or business-day
calendars. The JSON is this kit's input contract, not an iCalendar format.

## Why another set of tests?

The [RFC 5545 examples](https://www.rfc-editor.org/rfc/rfc5545#section-3.8.5.3)
and [dateutil's own test suite](https://github.com/dateutil/dateutil/blob/master/tests/test_rrule.py)
are valuable free alternatives with much broader coverage. This kit tests a
smaller set through a portable JSON contract so you can compare the same
expected occurrences across your application adapters. The inputs here are
synthetic; no customer calendars or external test files are bundled.

Expectations were reviewed against RFC 5545 sections 3.3.10, 3.8.5.1 and
3.8.5.3 and checked with python-dateutil 2.9.0.post0. Linux/Python 3.11,
six 1.17.0 and pinned tzdata 2025.2 produced 12/12 matching cases on
2026-09-25. The 13 comparator tests include deletion and insertion controls
for every case, duplicates, order errors and CLI exit codes. This does not
claim testing on Windows/macOS or on every recurrence library.

## A possible paid edition: is it useful to you?

The complete **0.1.0 release here stays free under MIT**, including commercial
use. A separate expanded pack is being evaluated at **US$19 once**: a fixed
version of 36 documented scenarios, Python and JavaScript adapters, and
integration notes for gaps/folds, all-day values and bounded query windows.
That edition is **not built or for sale yet**. There is no preorder, checkout,
subscription or promise of future updates. Payment and delivery terms would
be provided before any purchase.

If you tried the free kit in a calendar or scheduling project, please
[open a feedback issue](https://github.com/taroyamada3173-sys/rrule-boundary-kit/issues/new?template=feedback.md)
with your language/library, the case you ran, whether it helped, and whether
the proposed $19 edition would be worth buying. “The free alternatives are
enough” is equally useful. This is non-binding feedback. Do not post private
calendar data, email addresses, credentials or customer records. GitHub
issues are public; a synthetic case ID and a short description are enough.

AI tools assisted the code and documentation. The verification above is
limited to the named checks; no human review or customer adoption is claimed.

## License

MIT; see [LICENSE](LICENSE). Independent project, not affiliated with the
Python Software Foundation, dateutil or any calendar provider.
