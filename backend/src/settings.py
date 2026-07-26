"""미션 5 설정 — 로컬 MongoDB(.env) + 모델 outputs/."""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parents[1]


def _env(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name)
    if value is None or value == "":
        return default
    return value


def load_dotenv(path: Path | None = None) -> None:
    env_path = path or (ROOT / ".env")
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip("'").strip('"'))


load_dotenv()


def _resolve_path(value: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = ROOT / path
    return path.resolve()


# 미션 2와 동일한 이름·구조: outputs/<task>/final
OUTPUTS_DIR = _resolve_path(_env("OUTPUTS_DIR", "outputs") or "outputs")

# 소설 목록 폴백 (미션 2 inbox)
MISSION2_DIR = _resolve_path(
    _env("MISSION2_DIR", str(ROOT.parent / "mission2"))
    or str(ROOT.parent / "mission2")
)
NOVELS_DIR = _resolve_path(
    _env("NOVELS_DIR", str(MISSION2_DIR / "data" / "inbox" / "novels"))
    or str(MISSION2_DIR / "data" / "inbox" / "novels")
)

API_HOST = _env("API_HOST", "0.0.0.0") or "0.0.0.0"
API_PORT = int(_env("API_PORT", "8003") or "8003")

GENERATION = {
    "max_new_tokens": 200,
    "temperature": 0.8,
    "top_p": 0.92,
    "top_k": 50,
    "repetition_penalty": 1.15,
}

QA_PROMPT = (
    "당신은 한국 소설 전문가입니다.\n"
    "소설: {title}\n"
    "질문: {question}\n"
    "답변:"
)
SUMMARY_PROMPT = (
    "다음 한국 소설의 줄거리를 요약하세요.\n"
    "제목: {title}\n"
    "본문:\n{passage}\n"
    "줄거리:"
)
GEN_PROMPT = "제목: {title}\n소설:\n"


def model_dir(task: str) -> Path:
    return OUTPUTS_DIR / task / "final"


def get_mongo_settings() -> dict[str, str]:
    return {
        "host": _env("MONGO_HOST", "localhost") or "localhost",
        "port": _env("MONGO_PORT", "27017") or "27017",
        "db": _env("MONGO_DB", "mydb") or "mydb",
        "user": _env("MONGO_USER", "kogo3039") or "kogo3039",
        "password": _env("MONGO_PASSWORD", "math1106") or "math1106",
        "auth_source": _env("MONGO_AUTH_SOURCE", "admin") or "admin",
    }


def get_database_url() -> str:
    """MongoDB URI 반환."""
    if url := _env("DATABASE_URL") or _env("MONGO_URI"):
        return url
    s = get_mongo_settings()
    user = quote_plus(s["user"])
    password = quote_plus(s["password"])
    return (
        f"mongodb://{user}:{password}@{s['host']}:{s['port']}/{s['db']}"
        f"?authSource={s['auth_source']}"
    )


def get_db_name() -> str:
    if name := _env("MONGO_DB"):
        return name
    if url := _env("DATABASE_URL") or _env("MONGO_URI"):
        after_at = url.split("@", 1)[-1]
        path = after_at.split("/", 1)[-1] if "/" in after_at else ""
        db = path.split("?", 1)[0]
        if db:
            return db
    return "mydb"
