#!/usr/bin/env python3
"""
Wrapper script to run the ARM DVD Rip Organizer from command line.
Usage: python run.py
"""

import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path.parent))

# Run main
if __name__ == "__main__":
    from src.main import main

    sys.exit(main())
