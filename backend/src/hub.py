"""미션 2 파인튜닝 모델을 로드·캐시해 API에서 재사용합니다."""

from __future__ import annotations

from threading import Lock
from typing import Any

import torch

from modeling import generate_text, load_finetuned
from novels import find_novel
from settings import GENERATION, GEN_PROMPT, QA_PROMPT, SUMMARY_PROMPT, model_dir


def get_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


class ModelHub:
    def __init__(self) -> None:
        self.device = get_device()
        self._lock = Lock()
        self._bundle: dict[str, tuple[Any, Any]] = {}

    def ready(self, task: str) -> bool:
        return model_dir(task).exists()

    def status(self) -> dict[str, Any]:
        return {
            "device": str(self.device),
            "models": {
                task: {
                    "ready": self.ready(task),
                    "loaded": task in self._bundle,
                    "path": str(model_dir(task)),
                }
                for task in ("qa", "generation", "summary")
            },
        }

    def _ensure(self, task: str) -> tuple[Any, Any]:
        with self._lock:
            if task in self._bundle:
                return self._bundle[task]
            path = model_dir(task)
            if not path.exists():
                raise FileNotFoundError(
                    f"{task} 모델이 없습니다: {path}. "
                    "먼저 mission2에서 train 을 완료하세요."
                )
            tokenizer, model = load_finetuned(path)
            model.to(self.device)
            model.eval()
            self._bundle[task] = (tokenizer, model)
            return self._bundle[task]

    def _gen(
        self,
        task: str,
        prompt: str,
        *,
        max_new_tokens: int,
        temperature: float,
    ) -> str:
        tokenizer, model = self._ensure(task)
        g = GENERATION
        return generate_text(
            model,
            tokenizer,
            prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=g["top_p"],
            top_k=g["top_k"],
            repetition_penalty=g["repetition_penalty"],
            device=self.device,
        )

    def qa(self, title: str, question: str) -> str:
        prompt = QA_PROMPT.format(title=title, question=question)
        return self._gen("qa", prompt, max_new_tokens=120, temperature=0.3)

    def generate(
        self,
        title: str,
        seed_text: str = "",
        max_new_tokens: int | None = None,
    ) -> str:
        prompt = GEN_PROMPT.format(title=title)
        if seed_text:
            prompt += seed_text.strip() + " "
        return self._gen(
            "generation",
            prompt,
            max_new_tokens=max_new_tokens or GENERATION["max_new_tokens"],
            temperature=GENERATION["temperature"],
        )

    def summary(self, title: str, passage: str | None = None) -> str:
        if not passage:
            doc = find_novel(title)
            if not doc:
                raise ValueError(f"소설을 찾지 못했습니다: {title}")
            title = doc.title
            passage = doc.text
        prompt = SUMMARY_PROMPT.format(title=title, passage=passage[:350])
        return self._gen("summary", prompt, max_new_tokens=150, temperature=0.2)


_HUB: ModelHub | None = None


def get_hub() -> ModelHub:
    global _HUB
    if _HUB is None:
        _HUB = ModelHub()
    return _HUB
