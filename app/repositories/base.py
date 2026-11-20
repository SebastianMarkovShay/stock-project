from datetime import datetime
from typing import Protocol, Sequence

from app.domain.models import PriceSample # importing the data we just saved in models.py, so we can use it in the repository interface


class StockRepository(Protocol): #the contract for the repository, it defines the methods that any concrete implementation of the repository must have
    def initialize(self) -> None: #prepare the repository for use, e.g. create tables in a database
        ...

    def save_samples(self, samples: Sequence[PriceSample]) -> None: # save a list of price samples to the repository returns nothing
        ...

    def get_recent( # will get symbol and number of samples to retrieve, and return a list of PriceSample objects
        self,
        symbol: str,
        limit: int = 500,
    ) -> list[PriceSample]:
        ...

    def delete_before(self, cutoff: datetime) -> int:
        ...

    def ping(self) -> None: #check if the repository is reachable, e.g. if the database is up and running
        ...