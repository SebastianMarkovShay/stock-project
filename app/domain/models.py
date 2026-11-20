from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class PriceSample:
    symbol: str
    price: float
    timestamp: datetime

    def __post_init__(self) -> None:
        if not self.symbol or self.symbol != self.symbol.upper():
            raise ValueError("symbol must be a non-empty uppercase ticker")

        if self.price <= 0:
            raise ValueError("price must be positive")

        if self.timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")

    @property # just for convenience, we can get time in UTC without having to call astimezone() every time
    def timestamp_utc(self) -> datetime:
        return self.timestamp.astimezone(timezone.utc)