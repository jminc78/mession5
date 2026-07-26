from __future__ import annotations

from pydantic import BaseModel, Field


class QARequest(BaseModel):
    title: str = Field(..., min_length=1, examples=["소나기"])
    question: str = Field(..., min_length=1, examples=["주요 인물은 누구인가요?"])


class GenerateRequest(BaseModel):
    title: str = Field(..., min_length=1, examples=["가을 개울가의 만남"])
    seed_text: str = Field(default="", examples=["소년은 개울가에 앉아"])
    max_new_tokens: int | None = Field(default=None, ge=16, le=400)


class SummaryRequest(BaseModel):
    title: str = Field(..., min_length=1, examples=["메밀꽃필무렵"])
    passage: str | None = None


class TextResponse(BaseModel):
    result: str
    task: str
    title: str


class NovelItem(BaseModel):
    title: str
    file_stem: str
    author: str | None = None
    char_count: int | None = None


class HealthResponse(BaseModel):
    status: str
    outputs_dir: str
    models: dict
