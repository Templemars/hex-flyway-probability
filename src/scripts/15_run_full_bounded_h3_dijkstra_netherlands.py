#!/usr/bin/env python3
"""
Run the full bounded H3 Dijkstra behavior sweep for the Netherlands spring case.

This thin wrapper keeps an explicit Netherlands script in the numbered workflow
while reusing the shared population-aware implementation.
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().with_name("15_run_population_full_bounded_h3_dijkstra.py")


if __name__ == "__main__":
    sys.argv = [str(SCRIPT_PATH), "netherlands_spring"]
    runpy.run_path(str(SCRIPT_PATH), run_name="__main__")
