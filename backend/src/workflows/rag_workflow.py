from langgraph.graph import END, StateGraph

from src.agents.state import RAGState
from src.agents.planner import planner_agent
from src.agents.query import query_agent
from src.agents.retriever import retriever_agent
from src.agents.rerank import rerank_agent
from src.agents.reflection import reflection_agent
from src.agents.answer import answer_agent


def should_retry(state: RAGState) -> str:
    """Determine whether to retry retrieval or proceed to answer generation."""
    # If reflection passed, proceed to answer
    if state.get("reflection_passed", False):
        return "answer"
    # If max retries exceeded, proceed to answer with available documents
    if state.get("retry_count", 0) >= 1:
        return "answer"
    # Otherwise, retry with optimized query
    return "query_agent"


def build_rag_workflow() -> StateGraph:
    """Build the RAG workflow graph with all agents."""
    graph = StateGraph(RAGState)

    # Add agent nodes
    graph.add_node("planner", planner_agent)
    graph.add_node("query_agent", query_agent)
    graph.add_node("retriever", retriever_agent)
    graph.add_node("rerank", rerank_agent)
    graph.add_node("reflection", reflection_agent)
    graph.add_node("answer", answer_agent)

    # Define workflow edges
    graph.set_entry_point("planner")
    graph.add_edge("planner", "query_agent")
    graph.add_edge("query_agent", "retriever")
    graph.add_edge("retriever", "rerank")
    graph.add_edge("rerank", "reflection")

    # Conditional edge: retry or answer
    graph.add_conditional_edges(
        "reflection",
        should_retry,
        {"answer": "answer", "query_agent": "query_agent"}
    )

    graph.add_edge("answer", END)

    return graph.compile()


_rag_app = None


def get_rag_app():
    """Get or create RAG workflow instance (singleton)."""
    global _rag_app
    if _rag_app is None:
        _rag_app = build_rag_workflow()
    return _rag_app


async def warmup_rag():
    """Pre-warm the RAG workflow and models."""
    try:
        app = get_rag_app()
        # Trigger model loading
        from src.agents.planner import get_llm
        get_llm()
        return True
    except Exception:
        return False
