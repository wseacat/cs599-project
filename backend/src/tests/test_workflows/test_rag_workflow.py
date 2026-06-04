import pytest
from src.workflows.rag_workflow import build_rag_workflow


def test_build_rag_workflow():
    app = build_rag_workflow()
    assert app is not None


def test_rag_workflow_nodes():
    app = build_rag_workflow()
    nodes = app.get_graph().nodes
    expected_nodes = {"planner", "query_agent", "retriever", "rerank", "reflection", "answer"}
    assert expected_nodes.issubset(set(nodes))
