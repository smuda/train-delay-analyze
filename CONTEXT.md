# train-delay-analyze

Measures how late one SJ train, Stockholm C 17:21 to Umeå C 23:34,
arrives at its destination, as delay statistics over many days.

## Language

### Advertised arrival

The timetabled arrival time at Umeå C (23:34), as published.
_Avoid_: predicted arrival, scheduled time

### Estimated arrival

Trafikverket's running forecast of the arrival time while the train
is underway. Not used as a baseline for delay.
_Avoid_: predicted arrival, prognosis

### Arrival delay

Actual arrival time at Umeå C minus advertised arrival, in minutes.
_Avoid_: lateness, delay (unqualified)

### Delay bucket

An interval of arrival delay used to group trips in the delay
histogram. Each bucket includes its lower edge and excludes its
upper: [0, 6) is on time, then [6, 15), [15, 30), [30, 45), ...
Early arrivals fall in the first bucket. The buckets end with the
one holding the latest arrival.
_Avoid_: bin, interval

### Not arrived

A trip with no actual arrival at Umeå C: fully cancelled, terminated
short of Umeå, or replaced by a bus or another train. Counted as its
own category beside the delay histogram, never dropped.
_Avoid_: cancelled (too narrow), missing

### Train number

The number Trafikverket uses to identify a train run. The service is
identified by train number, each valid over a date range, not by
its departure time.
_Avoid_: train ID, departure (as an identifier)

### Service

The recurring Stockholm C 17:21 to Umeå C 23:34 train being studied,
spanning all days and all train numbers it has run under.
_Avoid_: the train, route

### Trip

One day's run of the service.
_Avoid_: journey, departure, run

### Announcement

One record from Trafikverket for a train at a station: an arrival or
departure, with its advertised and actual times. Kept exactly as
downloaded; statistics are always derived from stored announcements.
_Avoid_: event, record, row

### On time

A trip whose arrival delay is under 6 minutes (the official RT+5
rule: at most 5:59 late at the final station). Early counts as on
time.
_Avoid_: punctual, not late

### Location signature

Trafikverket's short code for a station or timing point, used in
every announcement. Always shown to people by the station's name,
never by the code. The service's advertised stops, in route order:

| Code | Station        |
|------|----------------|
| Cst  | Stockholm C    |
| Arnc | Arlanda C      |
| U    | Uppsala C      |
| Gä   | Gävle C        |
| Shv  | Söderhamn      |
| Hkl  | Hudiksvall     |
| Suc  | Sundsvall C    |
| Hsd  | Härnösand C    |
| Krf  | Kramfors       |
| Ök   | Örnsköldsvik C |
| Uåö  | Umeå Ö         |
| Uå   | Umeå C         |

_Avoid_: station code, abbreviation

### Advertised stop

A station where the service stops for passengers, as published in
the timetable. Other locations in the data are timing points the
train only passes.
_Avoid_: station (unqualified), halt

### Stretch

The part of a trip between two consecutive advertised stops, or the
time spent standing at one advertised stop.
_Avoid_: segment, leg, section

### Delay gained

How much later the train is at the end of a stretch than at its
start, in minutes. Negative means the train made up time.
_Avoid_: lost time, delay (unqualified)
