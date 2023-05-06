from typing import Optional, List

from marshmallow import EXCLUDE
from marshmallow_dataclass import dataclass as marshmallow_dataclass


@marshmallow_dataclass
class SampleTxnValue:
    txn_id: str
    client_id: str
    amount: float
    ccy: str
    balance: dict
    business_date: str

    class Meta:
        ordered = True
        unknown = EXCLUDE


@marshmallow_dataclass
class SampleTxnValueList:
    transactions: List[SampleTxnValue]

    class Meta:
        ordered = True
