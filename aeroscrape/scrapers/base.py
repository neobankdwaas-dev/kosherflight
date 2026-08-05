"""
Abstract Base Class for Flight Scrapers in AeroScrape.
"""
from abc import ABC, abstractmethod
from typing import List
from aeroscrape.models import FlightQuery, FlightResult


class FlightScraper(ABC):
    """
    Abstract base scraper class.
    All individual scraper adapters (Google Flights, Skyscanner, Direct Airline) inherit from this.
    """
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def search_flights(self, query: FlightQuery) -> List[FlightResult]:
        """
        Search flights for the given query and return a list of standardized FlightResult objects.
        """
        pass
