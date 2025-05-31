from loguru import logger

from deepwiki.workflow.state import ProcessingStage, DeepWikiState
from deepwiki.tools.repo_fetcher import fetch
from deepwiki.tools.code_parser import parse
from deepwiki.tools.code_analyzer import analyze
from deepwiki.tools.doc_generator import generate_docs
from deepwiki.tools.diagram_generator import create_diagrams
from deepwiki.tools.wiki_builder import build

from deepwiki.workflow.edges import should_parse_file

from deepwiki.rag.vector_store import vector_store

async def fetch_repository(state: DeepWikiState) -> DeepWikiState:
    """Fetch and clone the repository."""

    logger.info(f"Fetching repository: {state['repo_url']}")
    state["stage"] = ProcessingStage.FETCHING

    try:
        repo_data = await fetch(
            repo_url=state["repo_url"],
            repo_type=state["repo_type"]
        )
        state["repository"] = repo_data
        logger.info(f"Repository fetched successfully: {repo_data.name}")
    except Exception as e:
        logger.error(f"Error fetching repository: {e}")
        state["stage"] = ProcessingStage.ERROR
        state["error"] = str(e)

    return state

async def parse_code(state: DeepWikiState) -> DeepWikiState:
    """Parse all code files in the repository."""

    logger.info("Parsing code files")
    state["stage"] = ProcessingStage.PARSING

    try:
        repo = state["repository"]
        parsed_file = []
        for file_path in repo.files:
            if should_parse_file(file_path):
                parsed = await parse(file_path, repo.local_path)
                if parsed:
                    parsed_file.append(parsed)
                    await vector_store.add_code_file(parsed)
        
        state["repository"].files = parsed_file
        logger.info(f"Parsed {len(parsed_file)} code files")
    
    except Exception as e:
        logger.error(f"Error parsing code files: {e}")
        state["stage"] = ProcessingStage.ERROR
        state["error"] = str(e)
    
    return state

async def analyze_code(state: DeepWikiState) -> DeepWikiState:
    """Analyze code structure and dependencies."""
    logger.info("Analyzing code structure")
    state["stage"] = ProcessingStage.ANALYZING

    analysis_results = await analyze(state)
    state["code_analysis"] = analysis_results["analysis"]
    state["dependency_graph"] = analysis_results["dependencies"]
    state["architecture_summary"] = analysis_results["summary"]

    return state

async def generate_docs(state: DeepWikiState) -> DeepWikiState:
    """Generate comprehensive documents"""
    logger.info("Generating documentation")
    state["stage"] = ProcessingStage.GENERATING

    docs = await generate_docs(state)
    state["documents"] = docs

    return state

async def create_diagrams(state: DeepWikiState) -> DeepWikiState:
    """Create UML and architecture diagrams."""
    logger.info("Creating diagrams")
    state['stage'] = ProcessingStage.DIAGRAMMING
    
    diagrams = await create_diagrams(state)
    state['diagrams'] = diagrams
    
    return state

async def build_wiki(state: DeepWikiState) -> DeepWikiState:
    """Build the final wiki structure."""
    logger.info("Building wiki")
    state['stage'] = ProcessingStage.BUILDING
    
    wiki_data = await build(state)
    state['wiki_pages'] = wiki_data['pages']
    state['wiki_structure'] = wiki_data['structure']
    state['stage'] = ProcessingStage.COMPLETE
    
    logger.success("Wiki generation complete!")
    return state

async def handle_errors(state: DeepWikiState) -> DeepWikiState:
    """Handle errors in the workflow."""
    logger.error(f"Workflow error: {state['errors']}")
    state['stage'] = ProcessingStage.ERROR
    
    # Generate error report
    error_summary = "\n".join(state['errors'])
    state['documentation'] = {
        'error_report': f"# Wiki Generation Failed\n\n## Errors:\n{error_summary}"
    }
    
    return state