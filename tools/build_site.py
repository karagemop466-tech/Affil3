#!/usr/bin/env python3
"""Entry point: python3 tools/build_site.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build_core  # noqa: E402

if __name__ == "__main__":
    build_core.build()
