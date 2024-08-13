import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.utils import dict_to_proto_struct
import unittest

class TestGrpcIndex(unittest.TestCase):
    # The test methods here
    pass

if __name__ == '__main__':
    unittest.main()