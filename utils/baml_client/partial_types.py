###############################################################################
#
#  Welcome to Baml! To use this generated code, please run the following:
#
#  $ pip install baml-py
#
###############################################################################

# This file was generated by BAML: please do not edit it. Instead, edit the
# BAML files and re-generate this code.
#
# ruff: noqa: E501,F401,F821
# flake8: noqa: E501,F401,F821
# pylint: disable=unused-import,line-too-long
# fmt: off
import baml_py
from enum import Enum
from pydantic import BaseModel, ConfigDict
from typing_extensions import TypeAlias
from typing import Dict, Generic, List, Optional, TypeVar, Union, Literal

from . import types
from .types import Checked, Check

###############################################################################
#
#  These types are used for streaming, for when an instance of a type
#  is still being built up and any of its fields is not yet fully available.
#
###############################################################################

T = TypeVar('T')
class StreamState(BaseModel, Generic[T]):
    value: T
    state: Literal["Pending", "Incomplete", "Complete"]


class BulletPoints(BaseModel):
    points: List[str]
    mainIdea: Optional[str] = None
    complexity: Optional[Union[Literal["basic"], Literal["intermediate"], Literal["advanced"]]] = None

class ChatMessage(BaseModel):
    role: Optional[Union[Literal["user"], Literal["assistant"]]] = None
    content: Optional[str] = None
    timestamp: Optional[str] = None

class ChatResponse(BaseModel):
    answer: Optional[str] = None
    usedContext: List["ContextSource"]
    confidence: Optional[Union[Literal["high"], Literal["medium"], Literal["low"]]] = None

class ContextSource(BaseModel):
    sourceType: Optional[Union[Literal["vector_db"], Literal["document"], Literal["api"]]] = None
    content: Optional[str] = None
    relevanceScore: Optional[float] = None

class FinalResponse(BaseModel):
    answer: StreamState[Optional[str]]
    queryUsed: Optional[str] = None
    rawResults: Optional[str] = None

class GraphQuery(BaseModel):
    query: Optional[str] = None

class GraphResult(BaseModel):
    result: Optional[str] = None

class GraphSchema(BaseModel):
    nodes: List[str]
    relationships: List[str]
    properties: List[str]

class Resume(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    experience: List[str]
    skills: List[str]
