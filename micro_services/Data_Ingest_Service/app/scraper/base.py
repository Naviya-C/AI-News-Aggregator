from abc import ABC, abstractmethod

class BaseScraper(ABC):

    @abstractmethod
    def fetch(self):
        pass