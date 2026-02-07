#!/usr/bin/env python3

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cyberfind import run_gui  # noqa: E402

if __name__ == "__main__":
    run_gui()
