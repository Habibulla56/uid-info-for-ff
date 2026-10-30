# -*- coding: utf-8 -*-
# Minimal manual Protobuf definition for PlayerPersonalShow to avoid missing module errors

from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

_sym_db = _symbol_database.Default()

class PlayerPersonalShowReq(_message.Message):
    __slots__ = ["uid"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class PlayerPersonalShowRes(_message.Message):
    __slots__ = ["nickname", "level", "banner", "signature"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

_sym_db.RegisterMessage(PlayerPersonalShowReq)
_sym_db.RegisterMessage(PlayerPersonalShowRes)
