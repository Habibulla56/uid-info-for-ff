# -*- coding: utf-8 -*-
# Utility functions for encoding, decoding Protocol Buffers and loading data

import json
import os

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

def load_accounts(filepath="utilities/accounts.json"):
    """
    Loads accounts data from JSON file safely.
    """
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            print(f"Accounts file not found at {filepath}, returning empty list.")
            return []
    except Exception as e:
        print(f"Error loading accounts: {e}")
        return []
