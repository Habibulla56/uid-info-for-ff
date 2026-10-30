# -*- coding: utf-8 -*-
# Utility functions for encoding and decoding Protocol Buffers

def encode_protobuf(message_obj):
    """
    Encodes a protobuf message object into bytes.
    """
    try:
        return message_obj.SerializeToString()
    except Exception as e:
        print(f"Error encoding protobuf: {e}")
        return b""

def decode_protobuf(message_class, byte_data):
    """
    Decodes raw bytes into the specified protobuf message class.
    """
    try:
        msg = message_class()
        msg.ParseFromString(byte_data)
        return msg
    except Exception as e:
        print(f"Error decoding protobuf: {e}")
        return None
