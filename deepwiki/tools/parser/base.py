from abc import ABC, abstractmethod

class BaseLanguageParser(ABC):
    """
    Abstract base class for language parsers.
    """

    @abstractmethod
    def parse(self, content: str) -> tuple[list[str], list[str]]:
        """Parse code and return structured data."""
        pass
