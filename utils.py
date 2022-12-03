from __future__ import annotations
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field  # type:ignore


class Status(Enum):
    SUCCESS = 'success'
    FAIL = 'fail'


class CommonModel(BaseModel):
    stage: str
    detail: dict = Field(default_factory=dict)
    result: Status = Status.SUCCESS
    e: Optional[ExceptionModel] = None

    def when_except(self, e: Exception):
        self.result = Status.FAIL
        self.e = ExceptionModel.from_e(e)


class ExceptionModel(BaseModel):
    name: str
    detail: str

    @staticmethod
    def from_e(e: Exception) -> ExceptionModel:
        return ExceptionModel(
            name=str(e.__class__),
            detail=str(e),
        )


CommonModel.update_forward_refs()
