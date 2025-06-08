import fnmatch
from pathlib import Path

class GitignoreChecker:
    def __init__(self, directory: Path, gitignore_path: Path):
        """
        Initialize the GitignoreChecker with a specific directory and the path to a .gitignore file.

        Args:
            directory (Path): The directory to be checked.
            gitignore_path (Path): The path to the .gitignore file.
        """
        self.directory = directory
        self.gitignore_path = gitignore_path
        self.folder_patterns, self.file_patterns = self._load_gitignore_patterns()
    
    def _load_gitignore_patterns(self) -> tuple:
        """
        Load and parse the .gitignore file, then split the patterns into folder and file patterns.

        If the specified .gitignore file is not found, fall back to the default path.

        Returns:
            tuple: A tuple containing two lists - one for folder patterns and one for file patterns.
        """
        try:
            with open(self.gitignore_path, 'r', encoding="utf-8") as f:
                gitignore_content = f.read()
        except FileNotFoundError:
            # If the .gitignore file is not found, use the default path
            default_gitignore_path = Path(self.directory) / '.gitignore'
            with open(default_gitignore_path, 'r', encoding="utf-8") as f:
                gitignore_content = f.read()
        
        patterns = self._parse_gitignore(gitignore_content)
        return self._split_gitignore_patterns(patterns)
        
    @staticmethod
    def _parse_gitignore(gitignore_content: str) -> list:
        """
        Parse the content of a .gitignore file into folder and file patterns.

        Args:
            gitignore_content (str): The content of the .gitignore file.

        Returns:
            list: A list of patterns extracted from the .gitignore content.
        """
        patterns = []
        for line in gitignore_content.splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                patterns.append(line)
        return patterns

    @staticmethod
    def _split_gitignore_patterns(gitignore_patterns: list) -> tuple:
        """
        Split the .gitignore patterns into folder patterns and file patterns.

        Args:
            gitignore_patterns (list): A list of patterns from the .gitignore file.

        Returns:
            tuple: Two lists, one for folder patterns and one for file patterns.
        """
        folder_patterns = []
        file_patterns = []
        for pattern in gitignore_patterns:
            if pattern.endswith("/"):
                folder_patterns.append(pattern.rstrip("/"))
            else:
                file_patterns.append(pattern)
        return folder_patterns, file_patterns

    @staticmethod
    def _is_ignored(path: Path, patterns: list) -> bool:
        """
        Check if the given path matches any of the patterns.

        Args:
            path (Path): The path to check.
            patterns (list): A list of patterns to check against.

        Returns:
            bool: True if the path matches any pattern, False otherwise.
        """
        for pattern in patterns:
            if fnmatch.fnmatch(path, pattern):
                return True
        return False
    
    def check_files_and_folders(self) -> list:
        """
        Check all files and folders in the given directory against the split gitignore patterns.
        Return a list of files that are not ignored and have the '.py' extension.
        The returned file paths are relative to the self.directory.

        Returns:
            list: A list of paths to files that are not ignored and have the '.py' extension.
        """
        not_ignored_files = []
        base_path = Path(self.directory)

        for path in base_path.rglob('*'):
            # Skip if parent directory is ignored
            if any(self._is_ignored(p.name, self.folder_patterns)
                   for p in path.parents):
                continue

            # Handle files
            if path.is_file():
                if (not self._is_ignored(path.name, self.file_patterns) and
                        path.suffix == '.py'):
                    relative_path = path.relative_to(base_path)
                    not_ignored_files.append(str(relative_path))
        
        return not_ignored_files

gitignore_checker = GitignoreChecker('tmp/deepwiki_repos/chautuankien_PhilosoAgent', 'tmp/deepwiki_repos/chautuankien_PhilosoAgent/.gitignore')
not_ignored_files = gitignore_checker.check_files_and_folders()
print(not_ignored_files)