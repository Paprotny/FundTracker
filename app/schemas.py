from pydantic import BaseModel
from datetime import datetime

# -------------------------
# ASSET
# -------------------------
class AssetBase(BaseModel):
    symbol: str
    market: str
    currency: str
    type: str

class AssetCreate(AssetBase):
    pass  # used to POST

class AssetOut(AssetBase):
    id: int

    class Config:
        orm_mode = True
# -------------------------
# TRANSACTION
# -------------------------
class TransactionBase(BaseModel):
    quantity: float
    price: float
    date: datetime | None = None

class TransactionCreate(TransactionBase):
    pass

class TransactionOut(TransactionBase):
    id: int

    class Config:
        orm_mode = True

# -------------------------
# PRICE CACHE
# -------------------------
class PriceCacheBase(BaseModel):
    price: float
    timestamp: datetime | None = None

class PriceCacheCreate(PriceCacheBase):
    pass

class PriceCacheOut(PriceCacheBase):
    id: int

    class Config:
        orm_mode = True