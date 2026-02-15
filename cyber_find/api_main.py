#!/usr/bin/env python3

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cyber_find import run_api_server  # noqa: E402

if __name__ == "__main__":
    run_api_server()
