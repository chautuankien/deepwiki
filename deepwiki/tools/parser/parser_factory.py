from .base import BaseLanguageParser
from .python_parser import PythonParser
from .java_parser import JavaParser

class ParserFactory:
    _parsers = {
        'python': PythonParser,
        'java': JavaParser,
    }

    @classmethod
    def get_parser(cls, language: str) -> BaseLanguageParser:
        """Get the appropriate parser for the given language."""
        if language in cls._parsers:
            return cls._parsers[language]
        raise ValueError(f"No parser available for language: {language}")