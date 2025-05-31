from langgraph.graph import END, StateGraph
from deepwiki.workflow.nodes import (
    fetch_repository,
    parse_code,
    analyze_code,
    generate_docs,
    create_diagrams,
    build_wiki,
    handle_errors
)
from deepwiki.workflow.edges import check_fetch_result, check_parse_result
from deepwiki.workflow.state import DeepWikiState

def create_workflow_graph():
    """Builds a workflow graph for DeepWiki."""
    # Create the graph
    graph = StateGraph(DeepWikiState)

    # Add nodes
    graph.add_node("fetch_repository", fetch_repository)
    graph.add_node("parse_code", parse_code)
    graph.add_node("analyze_code", analyze_code)
    graph.add_node("generate_docs", generate_docs)
    graph.add_node("create_diagrams", create_diagrams)
    graph.add_node("build_wiki", build_wiki)
    graph.add_node("handle_errors", handle_errors)

    # Define the flow
    graph.set_entry_point("fetch_repository")
    graph.add_conditional_edges(
        "fetch_repository",
        check_fetch_result,
        {
            "continue": "parse_code",
            "error": "handle_errors",
        }
    )

    graph.add_conditional_edges(
        "parse_code",
        check_parse_result,
        {
            "continue": "analyze_code",
            "error": "handle_errors",
        }
    )

    graph.add_edge("analyze_code", "generate_docs")
    graph.add_edge("generate_docs", "create_diagrams")
    graph.add_edge("create_diagrams", "build_wiki")
    graph.add_edge("build_wiki", END)
    graph.add_edge("handle_errors", END)

    return graph

graph = create_workflow_graph().compile()
