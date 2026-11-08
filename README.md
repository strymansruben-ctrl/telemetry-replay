# Telemetry Replay

A Python command-line tool for reviewing sensor logs after a bench test. It groups high readings into alerts, identifies gaps in recording and exports a machine-readable JSON report.

## Run the demo

From this repository root, with Python 3.10 or later. No packages are required. Use `python3` in place of `python` if your system uses that command.

```sh
python replay.py examples/bench-temperature.csv --limit 70 --max-gap-ms 150
python -m unittest discover -s tests -v
```

The synthetic bench log contains seven samples. The scan finds three high-temperature alerts and a 500 ms interval between the samples at 300 and 800 ms. The first alert contains two readings and peaks at 76 °C.

## Input and alert rules

Give the tool a CSV headed `time_ms,value` with one sensor channel. Time is elapsed milliseconds and must be a strictly increasing nonnegative integer. Values must be finite numbers. Choose the limit in the units of your sensor.

- Readings at or above the limit start or extend an alert. A reading below the limit ends it.
- An interval longer than the allowed gap starts a separate alert if the next sample is also high.
- Each alert reports the first and last observed high sample, the count and the peak. The tool makes no estimate of what happened between observations.

This is an offline scanner. It only detects gaps between observed samples. The gap setting needs to account for the expected sampling interval and normal timing jitter.

## Files

- `replay.py` contains the scanner and JSON command-line interface.
- `examples/bench-temperature.csv` contains the synthetic log.
- `tests/test_replay.py` checks alert boundaries, gaps, quiet runs and malformed samples.
