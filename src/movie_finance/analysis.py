"""Selection-aware financial analysis with bootstrap uncertainty and sensitivity checks."""
from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from .reporting import publish_report

FEATURES = ['budget_adj', 'popularity', 'vote_average', 'runtime']
REQUIRED = FEATURES + ['revenue_adj', 'vote_count', 'release_year']


def prepare_movies(frame):
    missing = set(REQUIRED) - set(frame.columns)
    if missing:
        raise ValueError(f'Missing required columns: {sorted(missing)}')
    data = frame.drop_duplicates().copy()
    for col in REQUIRED:
        data[col] = pd.to_numeric(data[col], errors='coerce')
    finite = np.isfinite(data[REQUIRED]).all(axis=1)
    usable = finite & data.budget_adj.gt(0) & data.revenue_adj.gt(0) & data.runtime.gt(0)
    analysis = data.loc[usable].copy()
    if len(analysis) < 8:
        raise ValueError('At least eight usable records are required for the financial analysis.')
    audit = {'input_rows': len(frame), 'exact_duplicates_removed': len(frame) - len(data),
             'deduplicated_rows': len(data), 'usable_rows': len(analysis),
             'retained_percent': float(100 * len(analysis) / len(data))}
    return data, analysis, audit


def rank_interval(x, y, draws=1000, seed=42):
    """Paired-record percentile bootstrap for Spearman correlation."""
    x, y = np.asarray(x), np.asarray(y)
    point = float(spearmanr(x, y).statistic)
    if len(x) < 8 or not np.isfinite(point):
        return {'rho': point if np.isfinite(point) else None, 'ci95': None}
    rng = np.random.default_rng(seed)
    values = []
    for _ in range(draws):
        idx = rng.integers(0, len(x), len(x))
        if np.ptp(x[idx]) == 0 or np.ptp(y[idx]) == 0:
            continue
        values.append(float(spearmanr(x[idx], y[idx]).statistic))
    interval = np.quantile(values, [.025, .975]).tolist() if values else None
    return {'rho': point, 'ci95': interval}


def summarize(data, analysis, audit):
    samples = {'Main cohort': analysis,
               'At least 100 votes': analysis[analysis.vote_count >= 100],
               'Financial upper 1% excluded': analysis[(analysis.budget_adj <= analysis.budget_adj.quantile(.99)) & (analysis.revenue_adj <= analysis.revenue_adj.quantile(.99))],
               'Financial values at least $1,000': analysis[(analysis.budget_adj >= 1000) & (analysis.revenue_adj >= 1000)]}
    sensitivity = []
    for name, sample in samples.items():
        if len(sample) < 8:
            continue
        for feature in FEATURES:
            estimate = rank_interval(sample[feature], sample.revenue_adj)
            sensitivity.append({'sample': name, 'feature': feature, 'n': len(sample), **estimate})
    decades = []
    for decade, group in data.groupby((data.release_year // 10 * 10).rename('decade')):
        if pd.isna(decade):
            continue
        retained = int(group.index.isin(analysis.index).sum())
        decades.append({'decade': int(decade), 'source_records': len(group), 'usable_records': retained,
                        'retained_percent': float(100 * retained / len(group))})
    bounds = np.unique(analysis.budget_adj.quantile([0, .25, .5, .75, 1]).to_numpy())
    if len(bounds) < 3:
        raise ValueError('Budget values do not provide enough distinct quantile boundaries.')
    group = pd.qcut(analysis.budget_adj, q=4, labels=False, duplicates='drop')
    quartiles = []
    for q, sample in analysis.groupby(group):
        quartiles.append({'quartile': f'Q{int(q)+1}', 'n': len(sample), 'median_revenue_millions': float(sample.revenue_adj.median() / 1e6)})
    return {'audit': audit, 'sensitivity': sensitivity, 'coverage_by_decade': decades,
            'budget_quartiles': quartiles, 'bootstrap': {'draws': 1000, 'seed': 42, 'unit': 'movie record',
             'scope': 'Within-cohort uncertainty only; selection bias and franchise dependence are not removed.'}}


def report_spec(result):
    labels = {'budget_adj': 'Budget', 'popularity': 'Popularity', 'vote_average': 'Viewer rating', 'runtime': 'Runtime'}
    views = []
    for name in dict.fromkeys(r['sample'] for r in result['sensitivity']):
        rows = [r for r in result['sensitivity'] if r['sample'] == name]
        views.append({'label': name, 'kind': 'bar', 'unit': 'Spearman correlation',
         'series': [{'name': 'Correlation with adjusted revenue', 'points': [
             {'x': labels[r['feature']], 'y': r['rho'], 'low': r['ci95'][0] if r['ci95'] else None,
              'high': r['ci95'][1] if r['ci95'] else None} for r in rows]}]})
    views.append({'label': 'Coverage by release decade', 'kind': 'bar', 'unit': '% retained',
                  'series': [{'name': 'Usable financial records', 'points': [{'x': str(r['decade']), 'y': r['retained_percent']} for r in result['coverage_by_decade']]}]})
    a = result['audit']
    return {'title': 'Movie revenue: evidence and selection', 'subtitle': 'Strong relationships are only useful when the sample behind them is visible.',
     'category': 'Financial data / exploratory research', 'findings': [f'{a["usable_rows"]:,} of {a["deduplicated_rows"]:,} distinct records support the main financial comparison ({a["retained_percent"]:.2f}%).',
      'Four cohort definitions expose how filtering changes the measured relationships.',
      'Paired-record bootstrap intervals quantify within-cohort uncertainty without claiming to fix missing-data bias.'],
     'views': views, 'methodology': [{'title': 'Financial cohort', 'body': 'Exact duplicates are removed. The analysis requires finite values, positive adjusted budget and revenue, and positive runtime. Excluded observations remain counted in the coverage audit.'},
      {'title': 'Sensitivity and uncertainty', 'body': 'Each cohort has 1,000 fixed-seed paired-record bootstrap draws for Spearman correlation. Whiskers show the 95% percentile interval. Filters are recomputed before resampling.'},
      {'title': 'Decision boundary', 'body': 'This is descriptive research, not a pre-release revenue forecast. Audience measures may be observed after release. Revenue is not profit; missing costs and selective financial reporting limit commercial inference.'}],
     'notes': 'The public report contains aggregate statistics only. Movie-level records and text are not embedded.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('reports'))
    args = parser.parse_args()
    try:
        data, analysis, audit = prepare_movies(pd.read_csv(args.input))
        result = summarize(data, analysis, audit)
        publish_report(args.output, result, report_spec(result), [args.input])
    except (ValueError, OSError) as exc:
        parser.exit(2, f'Analysis failed: {exc}\n')


if __name__ == '__main__':
    main()
