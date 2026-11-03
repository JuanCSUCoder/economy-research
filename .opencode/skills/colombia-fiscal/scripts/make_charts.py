#!/usr/bin/env python3
"""Run the canonical chart builder in src/econ_research/make_charts.py.

The chart code is source-agnostic and lives outside the skill so reports and
other skills share one implementation. This wrapper keeps the documented
skill command working.
"""

from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
runpy.run_path(str(ROOT / "src" / "econ_research" / "make_charts.py"), run_name="__main__")
