from typing_extensions import TypedDict
from typing import Any
from enum import Enum
from pydantic import BaseModel, Field

class ProcessingStage(Enum):
    """Stages of processing in the DeepWiki workflow."""
    FETCHING = "fetching"
    PARSING = "parsing"
    ANALYZING = "analyzing"
    GENERATING = "generating"
    DIAGRAMMING = "diagramming"
    BUILDING = "building"
    COMPLETE = "complete"
    ERROR = "error"

class CodeFile(BaseModel):
    """Model representing a code file in a repository."""
    path: str = Field(None, description="Path to the code file")
    content: str = Field(None, description="Content of the code file")
    language: str = Field(None, description="Programming language of the code file")

    classes: list[str] = Field(default_factory=list, description="List of classes in the code file")
    functions: list[str] = Field(default_factory=list, description="List of functions in the code file")

class Repository(BaseModel):
    """Model representing a code repository."""
    url: str = Field(None, description="URL of the repository")
    name: str = Field(None, description="Name of the repository")
    local_path: str | None = Field(None, description="Local path to the repository")
    branch: str = Field("main", description="Branch to process")
    
    files: list[CodeFile] = Field(default_factory=list, description="List of code files in the repository")
    structure: dict[str, Any] = Field(default_factory=dict, description="Directory structure of the repository")
    languages: list[str, int] = Field(default_factory=list, description="List of programming languages used in the repository")

    total_files: int = Field(0, description="Total number of files in the repository")
    total_lines: int = Field(0, description="Total number of lines in the repository")

class Document(BaseModel):
    """Generated document model."""
    overview: str | None = Field(None, description="Overview of the repository")
    architecture: str | None = Field(None, description="Architecture summary of the repository")

class Diagram(BaseModel):
    """UML diagram model."""
    diagram_type: str = Field(None, description="Type of the diagram (e.g., class, sequence)")
    title: str = Field(None, description="Title of the diagram")
    content: str = Field(None, description="Content of the diagram in a suitable format (e.g., PlantUML, Mermaid)")
    svg: str = Field(None, description="SVG content of the diagram for rendering")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the diagram")

class WikiPage(BaseModel):
    """Individual wiki page model."""
    title: str = Field(None, description="Title of the wiki page")
    path: str = Field(None, description="Path to the wiki page")
    content: str = Field(None, description="Content of the wiki page")
    category: str = Field(None, description="Category of the wiki page (e.g., overview, architecture, diagrams)")
    children: list['WikiPage'] = Field(default_factory=list, description="List of child wiki pages")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the wiki page")


class DeepWikiState(TypedDict):
    """
    Main state object for the LangGraph workflow.
    
    This state is passed between all nodes in the graph and accumulates
    information as the agent processes the repository.
    """

    repo_url: str
    repo_type: str # github, gitlab, local

    # Processing stage
    stage: ProcessingStage

    # Repository information
    repository: Repository | None

    # Analysis results
    code_analysis: dict[str, Any]
    dependency_graph: dict[str, list[str]]
    architecture_summary: str | None

    # Generated documents
    documents: Document
    diagrams: list[Diagram]
    wiki_pages: list[WikiPage]
    wiki_structure: dict[str, Any]

    # Metadata and control
    errors: list[str]
    
    