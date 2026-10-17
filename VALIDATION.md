# Methods and validation

## Automated checks

The test suite currently contains **7 tests**. It covers duplicate removal, invalid/nonfinite finances, insufficient cohorts, paired-bootstrap determinism and sign, coverage denominators, report safety and source/report consistency.

```sh
python -m pip install -e ".[dev]"
python -m pytest -q
```

Tests use small synthetic fixtures to isolate failure cases. They are not performance benchmarks. The checked-in report is generated from the historical project data and records its own input hashes, code hashes and exact dependency versions in `docs/metrics.json`. A consistency test rejects a report whose recorded implementation hashes differ from the current source.

## Report checks

All comparison selectors, numerical tables and CSV downloads are checked in a browser at desktop and mobile widths. Reports use self-contained HTML, SVG and embedded aggregate JSON. The chart scrolls inside its own region on narrow screens. No external scripts or raw restricted datasets are loaded.

## Evaluation scope

The intervals quantify within-cohort sampling uncertainty; they do not fix selection bias or dependence between related films. Audience measures have unspecified observation dates and may be post-release. Revenue is not profit, and this analysis is not a pre-release prediction model.

## Reproduction boundaries

The current execution record uses Python 3.14.3 and the dependency versions saved alongside the results. Automated repository checks also target Python 3.11 and 3.12. Floating-point values and model outputs may vary by library/runtime version. External source files can change; compare input fingerprints before interpreting a difference as an implementation regression.
