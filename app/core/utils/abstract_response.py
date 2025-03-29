from typing import Generic, TypeVar, Union

from pydantic import BaseModel

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    code: int
    table: str
    status: str
    message: str
    data: Union[T, list]

    class Config:
        from_attributes = True
