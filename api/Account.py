# -*- coding: utf-8 -*-
import requests
import json
from Proto.compiled import MajorLogin_pb2
from utilities.until import encode_protobuf, decode_protobuf

def get_garena_token(uid, access_token):
    """
    Handles Garena token generation or retrieval logic.
    """
    try:
        # Your token implementation logic here
        pass
    except Exception as e:
        print(f"Error in get_garena_token: {e}")
        return None

def get_major_login(uid, access_token):
    """
    Handles major login requests using Protobuf encoding.
    """
    try:
        # Create request object using the manual/clean protobuf class
        req = MajorLogin_pb2.MajorLoginReq()
        req.uid = int(uid)
        req.access_token = str(access_token)
        
        # Encode using utility function
        payload_bytes = encode_protobuf(req)
        
        # Add your request dispatch/API call logic here
        return payload_bytes
    except Exception as e:
        print(f"Error in get_major_login: {e}")
        return None
