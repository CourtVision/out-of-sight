import os
import sys

# For pdoc to work together with conda env
sys.path.append(os.path.dirname(__file__))
# print(sys.path)

#__pdoc__ = {
#    'tests': False}

__all__ = [
  "utils",
  "utils.config",
]