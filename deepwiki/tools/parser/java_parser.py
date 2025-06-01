from .base import BaseLanguageParser

class JavaParser(BaseLanguageParser):
    async def parse(content: str) -> tuple[list[str], list[str]]:
        pass