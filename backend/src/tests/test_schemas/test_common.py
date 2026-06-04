from src.schemas.common import BaseResponse, PaginatedResponse


def test_base_response():
    response = BaseResponse()
    assert response.success is True
    assert response.message == ""


def test_base_response_custom():
    response = BaseResponse(success=False, message="Error")
    assert response.success is False
    assert response.message == "Error"


def test_paginated_response():
    response = PaginatedResponse()
    assert response.success is True
    assert response.total == 0
    assert response.page == 1
    assert response.page_size == 20


def test_paginated_response_custom():
    response = PaginatedResponse(total=100, page=2, page_size=50)
    assert response.total == 100
    assert response.page == 2
    assert response.page_size == 50
