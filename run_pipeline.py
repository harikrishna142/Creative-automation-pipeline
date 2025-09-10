#!/usr/bin/env python3
"""
Pipeline Runner - Simple script to run the creative automation pipeline
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# Change to the pipeline directory
pipeline_dir = src_dir / "pipeline"
os.chdir(pipeline_dir)

# Now import and run the main module
if __name__ == "__main__":
    import main
    main.cli()
