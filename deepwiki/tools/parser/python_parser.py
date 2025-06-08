import ast
from tqdm import tqdm
from pathlib import Path
from loguru import logger

from .base import BaseLanguageParser
from deepwiki.utils.gitignore_checker import GitignoreChecker

class PythonParser(BaseLanguageParser):
    def __init__(self, repo_path: Path, file_path: Path):
        """
        Initializes the parser with the repository path and the file path.

        Args:
            repo_path (Path): The root directory path of the repository.  
            file_path (Path): The path to the file, relative to the repository root. Set to None if want to parse all files in the repository.
        """
        self.file_path = file_path  # path relative to the root directory of the repository
        self.repo_path = repo_path
    
    def get_obj_code_info(
        self, code_type: str, code_name: str, start_line: int, end_line: int, params: list, file_path: Path = None
    ):
        """
        Get the code information for a given object.

        Args:
            code_type (str): The type of the code.
            code_name (str): The name of the code.
            start_line (int): The starting line number of the code.
            end_line (int): The ending line number of the code.
            parent (str): The parent of the code.
            file_path (Path, optional): The file path. Defaults to None.

        Returns:
            dict: A dictionary containing the code information.
        """

        code_info = {}
        code_info["type"] = code_type
        code_info["name"] = code_name
        code_info["md_content"] = []
        code_info["code_start_line"] = start_line
        code_info["code_end_line"] = end_line
        code_info["params"] = params

        with open(
            Path(self.repo_path)/ file_path if file_path != None else self.file_path,
            "r",
            encoding="utf-8",
        ) as code_file:
            lines = code_file.readlines()
            code_content = "".join(lines[start_line - 1 : end_line])
            # get position of the code name in the file
            name_column = lines[start_line - 1].find(code_name)
            # check if the code has a return statement
            if "return" in code_content:
                have_return = True
            else:
                have_return = False

            code_info["have_return"] = have_return
            code_info["code_content"] = code_content
            code_info["name_column"] = name_column

        return code_info

    def add_parent_references(self, node: ast.AST, parent: ast.AST = None) -> None:
        """
        Adds a parent reference to each node in the AST.
        Args:
            node: The AST node to process.
            parent: The parent node of the current node.
        """
        for child in ast.iter_child_nodes(node):
            child.parent = node
            self.add_parent_references(child, node)

    def get_functions_and_classes(self, content: str) -> list:
        """
        Retrieves all functions, classes, their parameters (if any), and their hierarchical relationships.
        Output Examples: [('FunctionDef', 'AI_give_params', 86, 95, None, ['param1', 'param2']), ('ClassDef', 'PipelineEngine', 97, 104, None, []), ('FunctionDef', 'get_all_pys', 99, 104, 'PipelineEngine', ['param1'])]
        On the example above, PipelineEngine is the Father structure for get_all_pys.

        Args:
            code_content: The code content of the whole file to be parsed.

        Returns:
            A list of tuples containing the type of the node (FunctionDef, ClassDef, AsyncFunctionDef),
            the name of the node, the starting line number, the ending line number, the name of the parent node, and a list of parameters (if any).
        """
        
        functions_and_classes: list = []

        try:
            tree = ast.parse(content)
            self.add_parent_references(tree)

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    if hasattr(node, 'lineno'):
                        start_line = node.lineno
                        end_line = getattr(node, 'end_lineno', None)
                    
                    params = (
                        [arg.arg for arg in node.args.args] if hasattr(node, 'args') else []
                    )

                    functions_and_classes.append(
                        (type(node).__name__, node.name, start_line, end_line, params)
                    )
            return functions_and_classes
        
        except SyntaxError as e:
            raise ValueError(f"Syntax error in Python code: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing Python code: {e}")
    
    def generate_file_structure(self, file_path: str) -> dict:
        """
        Generates a structured representation of the Python file, including functions and classes.

        Args:
            content: The code content of the whole file to be parsed.

        Returns:
            A dictionary containing the file structure with functions and classes.
        Output example:
        {
            "function_name": {
                "type": "function",
                "start_line": 10,
                ··· ···
                "end_line": 20,
                "parent": "class_name"
            },
            "class_name": {
                "type": "class",
                "start_line": 5,
                ··· ···
                "end_line": 25,
                "parent": None
            }
        }
        """
        with open(Path(self.repo_path)/file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            structures = self.get_functions_and_classes(content)
            file_objects = []  
            for struct in structures:
                structure_type, name, start_line, end_line, params = struct
                code_info = self.get_obj_code_info(
                    structure_type, name, start_line, end_line, params, file_path)
                file_objects.append(code_info)

        return file_objects


    def generate_overall_structure(self, jump_files: str) -> dict:

        repo_structure = {}
        gitignore_checker = GitignoreChecker(
            directory=self.repo_path,
            gitignore_path=Path(self.repo_path)/ ".gitignore",
        )

        bar = tqdm(gitignore_checker.check_files_and_folders())
        for not_ignored_files in bar:
            normal_file_names = not_ignored_files
            # if not_ignored_files in jump_files:
            #     print(
            #         f"{Fore.LIGHTYELLOW_EX}[File-Handler] Unstaged AddFile, ignore this file: {Style.RESET_ALL}{normal_file_names}"
            #     )
            #     continue
            # elif not_ignored_files.endswith(latest_verison_substring):
            #     print(
            #         f"{Fore.LIGHTYELLOW_EX}[File-Handler] Skip Latest Version, Using Git-Status Version]: {Style.RESET_ALL}{normal_file_names}"
            #     )
            #     continue
            # elif not_ignored_files.endswith(latest_version):
            #     """如果某文件被删除但没有暂存，文件系统有fake_file但没有对应的原始文件"""
            #     for k,v in file_path_reflections.items():
            #         if v == not_ignored_files and not os.path.exists(os.path.join(setting.project.target_repo, not_ignored_files)):
            #             print(f"{Fore.LIGHTYELLOW_EX}[Unstaged DeleteFile] load fake-file-content: {Style.RESET_ALL}{k}")
            #             normal_file_names = k #原来的名字
            #             break
            #     if normal_file_names == not_ignored_files:
            #         continue

            # if not_ignored_files in file_path_reflections.keys():
            #     not_ignored_files = file_path_reflections[not_ignored_files] #获取fake_file_path
            #     print(f"{Fore.LIGHTYELLOW_EX}[Unstaged ChangeFile] load fake-file-content: {Style.RESET_ALL}{normal_file_names}")

            try:
                repo_structure[normal_file_names] = self.generate_file_structure(
                    not_ignored_files
                )
            except Exception as e:
                logger.error(
                    f"Alert: An error occurred while generating file structure for {not_ignored_files}: {e}"
                )
                continue
            bar.set_description(f"Generating repo structure: {not_ignored_files}")
        return repo_structure
        

# python_parser = PythonParser(
#     repo_path="tmp/deepwiki_repos/chautuankien_PhilosoAgent", 
#     file_path=None
# )
# repo_structure = python_parser.generate_overall_structure(jump_files=[])
# print(repo_structure)
