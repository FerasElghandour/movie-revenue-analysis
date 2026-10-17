# TMDb Revenue and Movie Characteristics

Investigate the associations between inflation-adjusted movie revenue, budget, popularity, viewer rating and runtime in the supplied historical TMDb extract.

## Completion

Udacity project: **Investigate a Dataset**. Passed on **2026-10-11**, verified against the authenticated Udacity project-pass email. The receipt is kept privately.

This is a cleaned portfolio edition of the recovered implementation associated with that project. Udacity's email confirms the project passed; it does not certify this Git commit or identify the accepted archive by hash.

## Approach

Inspect missing and duplicate records, define usable financial observations, compare distributions and rank correlations, inspect budget quartiles, and repeat the comparisons under alternative sample definitions.

## Recorded results

The saved analysis starts with 10,866 records covering 1960–2015. Spearman correlations with adjusted revenue are 0.656 for budget, 0.608 for popularity, 0.240 for viewer rating and 0.284 for runtime. Only 35.47% of deduplicated records have usable values for the main comparison.

These figures come from saved execution records. Release validation is described in `VALIDATION.md`.

## Run

Release execution checks used Python 3.14.3; analysis dependency versions are pinned in `requirements.txt`.

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
jupyter lab
```

After supplying the historical CSV, open `Investigate_a_Dataset.ipynb` and run its cells from the repository root.

See [DATA.md](DATA.md) for inputs, attribution and excluded materials. Notebook outputs are cleared in this edition to exclude raw-data previews and machine-specific output.

## Limitations

Revenue is not profit. Zero financial values have uncertain meaning, the usable cohort is selective, and audience measures have unspecified collection times. There is no causal estimate or out-of-sample prediction claim.

## Provenance and rights

Prepared by Mohamed Feras Elghandour with AI assistance in implementation, debugging, analysis and documentation. This repository does not claim unaided coding or production deployment. Udacity supplied the educational context; third-party tools and inputs retain their own rights. Course lesson text, assessment prompts, rubrics, answer keys, pass-email bodies and authenticated classroom captures are excluded.

No new repository-wide software license is granted in this release. Existing third-party license notices remain applicable; see [DATA.md](DATA.md) and any `third_party/` or `vendor/` notices. This is an educational portfolio project, without a claim of Udacity endorsement.
