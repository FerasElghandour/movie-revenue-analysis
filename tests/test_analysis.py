import numpy as np
import pandas as pd
import pytest
from analysis import prepare_movies, rank_interval, summarize


def fixture_movies():
    return pd.DataFrame({'budget_adj': np.arange(1,17)*1e6,
                         'revenue_adj': np.arange(1,17)*3e6,
                         'runtime': np.arange(1,17)+85,
                         'vote_average': np.arange(1,17)/4+4,
                         'popularity': np.arange(1,17)/2,
                         'vote_count': [150]*16, 'release_year': list(range(1990,2006))})


def test_quality_gate_removes_duplicate_and_zero_financial_rows():
    raw = fixture_movies()
    raw.loc[0, 'budget_adj'] = 0
    raw = pd.concat([raw, raw.iloc[[2]]], ignore_index=True)
    _, valid, audit = prepare_movies(raw)
    assert audit['exact_duplicates_removed'] == 1
    assert audit['usable_rows'] == 15
    assert valid.budget_adj.gt(0).all()


def test_insufficient_financial_cohort_fails():
    raw = fixture_movies()
    raw['revenue_adj'] = 0
    with pytest.raises(ValueError, match='eight usable'):
        prepare_movies(raw)


def test_nonfinite_values_do_not_enter_cohort():
    raw = fixture_movies()
    raw.loc[0, 'popularity'] = np.inf
    _, _, audit = prepare_movies(raw)
    assert audit['usable_rows'] == 15


def test_rank_interval_is_deterministic_and_respects_pairing():
    x = np.arange(20)
    first = rank_interval(x, -x, draws=64)
    second = rank_interval(x, -x, draws=64)
    assert first == second
    assert first['rho'] == pytest.approx(-1)
    assert first['ci95'] == pytest.approx([-1,-1])


def test_coverage_denominator_includes_excluded_financial_records():
    raw = fixture_movies()
    raw.loc[:3, 'budget_adj'] = 0
    data, cohort, audit = prepare_movies(raw)
    result = summarize(data, cohort, audit)
    decade = next(r for r in result['coverage_by_decade'] if r['decade']==1990)
    assert decade['source_records'] == 10
    assert decade['usable_records'] == 6
    assert decade['retained_percent'] == 60
