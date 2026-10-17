"""Compatibility entry point; implementation lives in src/movie_finance."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from movie_finance.analysis import *

if __name__ == "__main__":
    main()
