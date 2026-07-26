"""Mission 5 FastAPI — 문답·생성·요약 API."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from hub import get_hub
from novels import load_novel_docs
from schemas import (
    GenerateRequest,
    HealthResponse,
    NovelItem,
    QARequest,
    SummaryRequest,
    TextResponse,
)
from settings import OUTPUTS_DIR

hub = get_hub()

app = FastAPI(
    title="Mission 5 API",
    description="한국 소설 Transformer API (문답 / 생성 / 줄거리)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
def health():
    st = hub.status()
    return HealthResponse(
        status="ok",
        outputs_dir=str(OUTPUTS_DIR),
        models=st["models"],
    )


@app.get("/api/novels", response_model=list[NovelItem])
def list_novels():
    try:
        docs = load_novel_docs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    return [
        NovelItem(
            title=d.title,
            file_stem=d.file_stem,
            author=d.author,
            char_count=d.char_count,
        )
        for d in docs
    ]


@app.post("/api/qa", response_model=TextResponse)
def api_qa(body: QARequest):
    try:
        result = hub.qa(body.title.strip(), body.question.strip())
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    return TextResponse(result=result, task="qa", title=body.title)


@app.post("/api/generate", response_model=TextResponse)
def api_generate(body: GenerateRequest):
    try:
        result = hub.generate(
            body.title.strip(),
            seed_text=body.seed_text or "",
            max_new_tokens=body.max_new_tokens,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    return TextResponse(result=result, task="generation", title=body.title)


@app.post("/api/summary", response_model=TextResponse)
def api_summary(body: SummaryRequest):
    try:
        result = hub.summary(body.title.strip(), passage=body.passage)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    return TextResponse(result=result, task="summary", title=body.title)
