#tests/unit/test_grpc_index.py
import sys
import os

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

print("Python path:", sys.path)
print("Current working directory:", os.getcwd())
print("Project root:", project_root)

from core.utils import dict_to_proto_struct
import unittest

class TestGrpcIndex(unittest.TestCase):
    def test_dict_to_proto_struct(self):
        # Add your test cases here
        pass

if __name__ == '__main__':
    unittest.main()



