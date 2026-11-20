from pathlib import Path # build in class for working with file paths


SYMBOLS: tuple[str, ...] = ("AAPL", "MSFT", "NVDA")
SAMPLE_INTERVAL_SECONDS: int = 5 * 60
RETENTION_DAYS: int = 3
DATABASE_PATH: Path = Path("data") / "stocks.sqlite3"