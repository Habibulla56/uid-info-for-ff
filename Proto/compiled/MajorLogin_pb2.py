# -*- coding: utf-8 -*-
# Minimal manual Protobuf definition for MajorLogin to avoid parsing errors

from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

_sym_db = _symbol_database.Default()

class MajorLoginReq(_message.Message):
    __slots__ = ["access_token", "uid"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class MajorLoginRes(_message.Message):
    __slots__ = ["serverUrl", "token", "code"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# Register message classes so they work seamlessly with protobuf serialization/deserialization
_sym_db.RegisterMessage(MajorLoginReq)
_sym_db.RegisterMessage(MajorLoginRes)
