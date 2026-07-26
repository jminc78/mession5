from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import torch
from transformers import AutoModelForCausalLM, GenerationConfig, PreTrainedTokenizerFast


_STOP_PATTERNS = [
    r"\n질문\s*:",
    r"\n답변\s*:",
    r"\n소설\s*:",
    r"\n제목\s*:",
    r"\n본문\s*:",
    r"\n줄거리\s*:",
    r"\n당신은 ",
]


def _cut_completion(text: str) -> str:
    """이어 생성되는 다음 프롬프트 조각을 잘라냅니다."""
    cut_at = len(text)
    for pat in _STOP_PATTERNS:
        m = re.search(pat, text)
        if m:
            cut_at = min(cut_at, m.start())
    return text[:cut_at].strip()


def load_tokenizer(model_name_or_path: str):
    """
    KoGPT2는 AutoTokenizer가 GPT2Tokenizer(영문 BPE)로 잘못 잡히는 경우가 있어
    PreTrainedTokenizerFast를 강제합니다.
    """
    path = str(model_name_or_path)
    local = Path(path)
    kwargs: dict[str, str] = {}
    # 허브 원본 로드 시 SKT 공식 special token을 명시
    if not (local.exists() and (local / "tokenizer.json").exists()):
        kwargs = {
            "bos_token": "</s>",
            "eos_token": "</s>",
            "unk_token": "<unk>",
            "pad_token": "<pad>",
            "mask_token": "<mask>",
        }
    tokenizer = PreTrainedTokenizerFast.from_pretrained(path, **kwargs)

    if tokenizer.pad_token is None:
        vocab = tokenizer.get_vocab() or {}
        if "<pad>" in vocab:
            tokenizer.pad_token = "<pad>"
        elif tokenizer.eos_token is not None:
            tokenizer.pad_token = tokenizer.eos_token
        else:
            tokenizer.add_special_tokens({"pad_token": "<pad>"})
    if tokenizer.eos_token is None:
        tokenizer.eos_token = "</s>"
    if tokenizer.bos_token is None:
        tokenizer.bos_token = tokenizer.eos_token
    return tokenizer


def load_model(model_name: str, tokenizer=None):
    model = AutoModelForCausalLM.from_pretrained(model_name)
    if tokenizer is not None:
        embed_size = model.get_input_embeddings().weight.size(0)
        if len(tokenizer) != embed_size:
            model.resize_token_embeddings(len(tokenizer))
        model.config.pad_token_id = tokenizer.pad_token_id
        model.config.eos_token_id = tokenizer.eos_token_id
        model.config.bos_token_id = tokenizer.bos_token_id
    return model


def load_finetuned(model_dir: str | Path):
    model_dir = Path(model_dir)
    tokenizer = load_tokenizer(str(model_dir))
    model = AutoModelForCausalLM.from_pretrained(model_dir)
    if model.config.pad_token_id is None:
        model.config.pad_token_id = tokenizer.pad_token_id
    return tokenizer, model


def generate_text(
    model,
    tokenizer,
    prompt: str,
    *,
    max_new_tokens: int = 200,
    temperature: float = 0.8,
    top_p: float = 0.92,
    top_k: int = 50,
    repetition_penalty: float = 1.15,
    device: str | Any = "cpu",
) -> str:
    model.eval()
    # MPS에서 sampling NaN이 나는 경우가 있어, 불안정하면 CPU로 폴백합니다.
    device = torch.device(device) if not isinstance(device, torch.device) else device
    try_devices = [device]
    if device.type == "mps":
        try_devices.append(torch.device("cpu"))

    last_err: Exception | None = None
    for dev in try_devices:
        try:
            model.to(dev)
            inputs = tokenizer(prompt, return_tensors="pt")
            inputs = {k: v.to(dev) for k, v in inputs.items()}
            do_sample = temperature is not None and temperature > 0
            gen_cfg = GenerationConfig(
                max_new_tokens=max_new_tokens,
                do_sample=do_sample,
                temperature=max(float(temperature), 1e-5) if do_sample else None,
                top_p=top_p if do_sample else None,
                top_k=top_k if do_sample else None,
                repetition_penalty=repetition_penalty,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )
            with torch.no_grad():
                output_ids = model.generate(**inputs, generation_config=gen_cfg)
            # 프롬프트 문자열 매칭 대신 '새로 생긴 토큰'만 디코딩
            prompt_len = inputs["input_ids"].shape[-1]
            new_tokens = output_ids[0][prompt_len:]
            completion = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
            return _cut_completion(completion)
        except RuntimeError as e:
            last_err = e
            msg = str(e).lower()
            if "nan" in msg or "inf" in msg or "probability" in msg:
                continue
            raise
    raise RuntimeError(f"생성 실패: {last_err}")
