from src.schemas.retrieval import RetrievalDebugResponse, SearchRequest, SearchResponse


def test_retrieval_debug_response():
    response = RetrievalDebugResponse(
        query="test query",
        plan="test plan",
        original_query="test query",
        rewritten_query="optimized query",
        expanded_queries=["query 1", "query 2"],
        retrieved_documents=[{"id": 1}],
        reranked_documents=[{"id": 1}],
        reflection_result="passed",
        retry_count=0,
    )
    assert response.query == "test query"
    assert response.plan == "test plan"
    assert response.rewritten_query == "optimized query"
    assert len(response.expanded_queries) == 2
    assert len(response.retrieved_documents) == 1


def test_retrieval_debug_response_defaults():
    response = RetrievalDebugResponse(query="test")
    assert response.query == "test"
    assert response.plan is None
    assert response.original_query is None
    assert response.rewritten_query is None
    assert response.expanded_queries == []
    assert response.retrieved_documents == []
    assert response.reranked_documents == []
    assert response.reflection_result is None
    assert response.retry_count == 0


def test_search_request():
    request = SearchRequest(query="test", top_k=5, collection="test_collection")
    assert request.query == "test"
    assert request.top_k == 5
    assert request.collection == "test_collection"


def test_search_request_defaults():
    request = SearchRequest(query="test")
    assert request.query == "test"
    assert request.top_k == 10
    assert request.collection is None


def test_search_response():
    response = SearchResponse(
        results=[{"id": 1}],
        query="test",
        total=1,
    )
    assert len(response.results) == 1
    assert response.query == "test"
    assert response.total == 1
