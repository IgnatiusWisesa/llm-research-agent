# tests/conftest.py

import sys
import os

# ✅ Ensure the `src/` directory is included in Python's import path.
# This allows test files to import modules using:
#     from agent.nodes.xxx import ...
# ...without needing to restructure directories or run from root every time.

# __file__ refers to this conftest.py file's path, i.e., tests/conftest.py
# os.path.dirname(__file__) = "tests/"
# "../src" will then resolve to the "src/" directory above.

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
