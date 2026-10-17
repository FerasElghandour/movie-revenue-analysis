"""Offline example using the public implementation; see README for evidence scope."""
import sys,json,pathlib,os
repo=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(repo));sys.path.insert(0,str(repo/'src'));os.chdir(repo)
import numpy as np,pandas as pd
from movie_finance.analysis import prepare_movies,rank_interval
raw=pd.DataFrame({'budget_adj':np.arange(1,17)*1e6,'revenue_adj':np.arange(1,17)*3e6,'runtime':np.arange(1,17)+85,'vote_average':np.arange(1,17)/4+4,'popularity':np.arange(1,17)/2,'vote_count':[150]*16,'release_year':list(range(1990,2006))})
raw.loc[0,'budget_adj']=0
_,valid,audit=prepare_movies(raw)
print(json.dumps({"fixture":"generated linear relationship, not movie evidence","audit":audit,"rank":rank_interval(valid.budget_adj,valid.revenue_adj,draws=64)}))
