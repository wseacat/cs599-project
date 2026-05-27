from pydantic import BaseModel


class BaseResponse(BaseModel):
    success: bool = True
    message: str = ""


class PaginatedResponse(BaseResponse):
    total: int = 0
    page: int = 1
    page_size: int = 20
