import ast

from .base import BaseLanguageParser

class PythonParser(BaseLanguageParser):
    async def parse(content: str) -> tuple[list[str], list[str]]:
        """"Use Python's built-in ast module to parse Python code."""
        
        classes = []
        functions = []

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):     
                    # Skip methods that are part of a class
                    if node.args.args and node.args.args[0].arg != 'self':
                        functions.append(node.name)
            
            return classes, functions
        
        except SyntaxError as e:
            raise ValueError(f"Syntax error in Python code: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing Python code: {e}")
