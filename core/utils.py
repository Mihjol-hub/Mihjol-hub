# core/utils.py

from google.protobuf.struct_pb2 import Struct

def dict_to_proto_struct(data):
    """
    Convert a Python dictionary to a Protobuf Struct.
    """
    struct = Struct()
    struct.update(data)
    return struct

# Add any other utility functions here