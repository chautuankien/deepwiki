from pathlib import Path
from loguru import logger

from deepwiki.config import settings
from .parser.parser_factory import ParserFactory

async def parse(file_path: str, local_path: str) -> dict:
    try:
        full_path = Path(local_path) / file_path
        if not full_path.exists():
            logger.error(f"File not found: {full_path}")
            raise FileNotFoundError(f"File not found: {full_path}")
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            logger.error(f"Failed to read file {full_path} due to encoding issues.")
            raise ValueError(f"Failed to read file {full_path} due to encoding issues.")
        
        # Detect language
        ext = full_path.suffix.lower()
        language = settings.LANGUAGE_MAP.get(ext, "unknown")

        # Get appropriate parser
        parser = ParserFactory.get_parser(language)

        classes, functions = await parser.parse(content=content)

        # Remove duplicates while preserving order
        classes = list(dict.fromkeys(classes))
        functions = list(dict.fromkeys(functions))

        # Create a structured result
        result = {
            "path": str(full_path),
            "content": content,
            "language": language,
            "classes": classes,
            "functions": functions
        }
        logger.info(f"Parsed {file_path} successfully with {len(classes)} classes and {len(functions)} functions.")

        return result
    
    except Exception as e:
        logger.error(f"Error parsing file {file_path}: {e}")
        raise ValueError(f"Error parsing file {file_path}: {e}")