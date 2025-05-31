from loguru import logger
from pathlib import Path
from git import Repo
from urllib.parse import urlparse
from typing import Any
import shutil
import asyncio
import os

from deepwiki.workflow.state import Repository, CodeFile
from deepwiki.config import settings


async def fetch(repo_url: str, repo_type: str = "github") -> Repository:
    """
    Fetch the repository from the specified source.
    
    Args:
        repo_url (str): URL of the repository.
        repo_type (str): Type of repository (github, gitlab, local).
    
    Returns:
        Repository: The fetched repository object.
    """
    if repo_type == "local":
        return await _fetch_local(repo_url)
    elif repo_type in ["github", "gitlab"]:
        return await _fetch_git(repo_url, repo_type)
    else:
        raise ValueError(f"Unsupported repository type: {repo_type}")

async def _fetch_local(local_path: str) -> Repository:
    """
    Fetch a local repository.
    
    Args:
        local_path (str): Path to the local repository.
    
    Returns:
        Repository: The fetched local repository object.
    """
    pass

async def _fetch_git(repo_url: str, repo_type: str) -> Repository:
    """Fetch a Git repository"""
    # Parse the repository URL
    parsed_url = urlparse(repo_url)
    path_parts = parsed_url.path.strip("/").split("/")

    if len(path_parts) < 2:
        raise ValueError(f"Invalid {repo_type} repository URL: {repo_url}")
    
    # Extract owner and repository name
    owner = path_parts[0]
    repo_name = path_parts[1].replace(".git", "")

    # Create temporary directory for cloning
    clone_dir = settings.temp_dir / f"{owner}_{repo_name}"

    # Remove existing clone directory if it exists
    if clone_dir.exists():
        shutil.rmtree(clone_dir) 

    # Clone the repository
    try:
        logger.info(f"Cloning {repo_type} repository: {repo_url} into {clone_dir}")
        
        # Use async subprocess for cloning
        process = await asyncio.create_subprocess_exec(
            "git", "clone", "--depth=1", repo_url, str(clone_dir),
            stdout=asyncio.subprocess.PIPE, # capture stdout
            stderr=asyncio.subprocess.PIPE  # capture stderr
        )

        # Wait with a timeout
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=settings.clone_timeout
            )
        except asyncio.TimeoutError:
            process.kill()
            raise TimeoutError(f"Cloning {repo_type} repository timed out after {settings.clone_timeout} seconds")

        # Check if the process completed successfully
        if process.returncode != 0:
            raise RuntimeError(f"Failed to clone {repo_type} repository: {stderr.decode()}")
    
        # Get branch info
        git_repo = Repo(clone_dir)
        branch = git_repo.active_branch.name

        # Build repository object
        repo = Repository(
            url=repo_url,
            name=repo_name,
            local_path=str(clone_dir),
            branch=branch,
        )

        # Scan files
        files = await _scan_directory(clone_dir)
        repo.files = files
        repo.total_files = len(files)

        # Calculate language statistics
        repo.languages = await _calculate_languages(files)
        
        # Build directory structure
        repo.structure = await _build_structure(clone_dir)
        
        logger.success(f"Successfully cloned repository: {repo.name}")
        return repo


    except Exception as e:
        # Clean up on error
        if clone_dir.exists():
            shutil.rmtree(clone_dir)
        raise e

    
async def _scan_directory(path: Path) -> list[CodeFile]:
    """Scan directory and return list of code files"""
    files = []
    excluded_dirs = set(settings.excluded_dirs)
    excluded_extensions = set(settings.excluded_extensions)

    for root, dirs, filenames in os.walk(path):
        # Exclude directories
        dirs[:] = [d for d in dirs if d not in excluded_dirs] # dir[:] modifies the same dirs object in place

        for filename in filenames:
            if any(filename.endswith(ext) for ext in excluded_extensions):
                continue
            
            file_path = Path(root) / filename
            relative_path = file_path.relative_to(path)
            # files.append(CodeFile(
            #     path=str(relative_path),
            # ))
            files.append(relative_path)

    return files

async def _calculate_languages(files: list[CodeFile]) -> dict[str, int]:
    """Calculate language statistics from file extensions."""
    language_map = {
        ".py": "Python",
        ".js": "JavaScript", 
        ".ts": "TypeScript",
        ".java": "Java",
        ".go": "Go",
        ".rs": "Rust",
        ".cpp": "C++",
        ".c": "C",
        ".cs": "C#",
        ".rb": "Ruby",
        ".php": "PHP",
        ".swift": "Swift",
        ".kt": "Kotlin",
        ".scala": "Scala",
        ".r": "R",
        ".m": "MATLAB",
        ".jl": "Julia",
        ".vue": "Vue",
        ".jsx": "React",
        ".tsx": "TypeScript React"
    }
    
    languages = {}
    # Iterate through files and count number of languages based on extensions
    for file in files:
        ext = Path(file).suffix.lower()
        if ext in language_map:
            lang = language_map[ext]
            languages[lang] = languages.get(lang, 0) + 1
    
    # Sort by count
    return dict(sorted(languages.items(), key=lambda x: x[1], reverse=True))

async def _build_structure(path: Path) -> dict[str, Any]:
    """Build hierarchical directory structure."""
    structure = {"name": path.name, "type": "directory", "children": []}
    
    # Build tree recursively
    await _build_structure_recursive(path, structure, max_depth=5)
    
    return structure

async def _build_structure_recursive(
    path: Path,
    node: dict[str, Any],
    current_depth: int = 0,
    max_depth: int = 5
):
    """Recursively build directory structure."""
    if current_depth >= max_depth:
        return
    
    try:
        items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        
        for item in items:
            if item.name.startswith(".") and item.name != ".github":
                continue
            
            if item.is_dir():
                if item.name in ["node_modules", "__pycache__", "venv"]:
                    continue
                    
                child_node = {
                    "name": item.name,
                    "type": "directory",
                    "children": []
                }
                node["children"].append(child_node)
                
                # Recurse
                await _build_structure_recursive(
                    item, child_node, current_depth + 1, max_depth
                )
            else:
                # Add file
                node["children"].append({
                    "name": item.name,
                    "type": "file",
                    "size": item.stat().st_size # get file size in bytes
                })
                
    except PermissionError:
        pass