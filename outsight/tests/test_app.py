import sys
import os
from pathlib import Path
import unittest
module_path = Path(os.path.join(Path(__file__).parents[2], 'outsight')).absolute()
sys.path.append(str(module_path))  
import app

class TestImport(unittest.TestCase):
    """
    Our basic test class
    """
    def test_run(self):
        """
        The actual test.
        Any method which starts with ``test_`` will considered as a test case.
        """
        if app:
            expr = True
        else:
            expr = False
        self.assertTrue(expr)

if __name__ == '__main__':
    unittest.main()