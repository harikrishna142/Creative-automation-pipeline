#!/usr/bin/env python3
"""Test the method signature"""

import sys
from pathlib import Path

# Add src to path
src_dir = Path("src")
sys.path.insert(0, str(src_dir))

try:
    from pipeline.asset_generator import AssetGenerator
    import inspect
    
    # Get method signature
    method = getattr(AssetGenerator, 'generate_product_image')
    sig = inspect.signature(method)
    print(f"Method signature: {sig}")
    
    # Get parameter names
    params = list(sig.parameters.keys())
    print(f"Parameters: {params}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

