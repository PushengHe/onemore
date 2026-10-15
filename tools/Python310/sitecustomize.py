import os
import sys

script = sys.argv[0]
if script and script != "-c":
    script_dir = os.path.dirname(os.path.abspath(script))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
