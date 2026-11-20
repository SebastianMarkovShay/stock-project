from contextlib import closing
import sqlite3 #python basic model for working with SQLite databases
from pathlib import Path
from datetime import datetime, timezone
from typing import Sequence

from app.domain.models import PriceSample


class SQLiteStockRepository: #implementation of the contract defined in StockRepository, using SQLite as the storage backend
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def _connect(self) -> sqlite3.Connection:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(self.database_path, timeout=10)

    def initialize(self) -> None:
        with closing(self._connect()) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS price_samples (
                    symbol TEXT NOT NULL,
                    price REAL NOT NULL CHECK (price > 0),
                    timestamp TEXT NOT NULL,
                    PRIMARY KEY (symbol, timestamp)
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_price_samples_symbol_timestamp
                ON price_samples (symbol, timestamp DESC)
                """
            )

            connection.commit()


    def save_samples(self, samples: Sequence[PriceSample]) -> None:
        rows = [
            (
                sample.symbol,
                sample.price,
                sample.timestamp_utc.isoformat(),
            )
            for sample in samples
        ]

        if not rows:
            return

        with closing(self._connect()) as connection:
            connection.executemany(
                """
                INSERT INTO price_samples (symbol, price, timestamp)
                VALUES (?, ?, ?)
                ON CONFLICT(symbol, timestamp)
                DO UPDATE SET price = excluded.price
                """,
                rows,
            )
            connection.commit()

    def get_recent(
        self,
        symbol: str,
        limit: int = 500,
    ) -> list[PriceSample]:
        if limit <= 0:
            raise ValueError("limit must be positive")

        with closing(self._connect()) as connection:
            rows = connection.execute(
                """
                SELECT symbol, price, timestamp
                FROM price_samples
                WHERE symbol = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (symbol.upper(), limit),
            ).fetchall()

        return [
            PriceSample(
                symbol=row[0],
                price=row[1],
                timestamp=datetime.fromisoformat(row[2]).astimezone(timezone.utc),
            )
            for row in rows
        ]

    def delete_before(self, cutoff: datetime) -> int:
        if cutoff.tzinfo is None:
            raise ValueError("cutoff must be timezone-aware")

        cutoff_utc = cutoff.astimezone(timezone.utc).isoformat()

        with closing(self._connect()) as connection:
            cursor = connection.execute(
                """
                DELETE FROM price_samples
                WHERE timestamp < ?
                """,
                (cutoff_utc,),
            )
            deleted_count = cursor.rowcount
            connection.commit()

        return deleted_count

    def ping(self) -> None:
        with closing(self._connect()) as connection:
            connection.execute("SELECT 1").fetchone()