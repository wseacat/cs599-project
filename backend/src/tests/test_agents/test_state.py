from src.agents.state import RAGState


def test_rag_state_keys():
    expected_keys = {
        "original_query", "rewritten_query", "expanded_queries",
        "retrieval_plan", "retrieved_documents", "reranked_documents",
        "reflection_result", "reflection_passed", "retry_count",
        "final_answer", "citations", "chat_history",
        "conversation_id", "message_id", "workflow_trace",
    }
    annotations = RAGState.__annotations__
    assert expected_keys == set(annotations.keys())
