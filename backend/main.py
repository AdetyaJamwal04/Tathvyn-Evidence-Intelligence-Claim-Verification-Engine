"""Tathvyn - Entry Point Wrapper.

Delegates execution to the internal tathvyn.cli dispatcher.
"""

import sys
from pathlib import Path

# Ensure src is on sys.path
src_dir = Path(__file__).resolve().parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from tathvyn.cli import main

if __name__ == "__main__":
    main()
