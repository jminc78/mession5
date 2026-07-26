#!/usr/bin/env python3
"""Mission 5 — Backend API (문답·생성·요약)."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _ensure_env() -> None:
    env = ROOT / ".env"
    example = ROOT / ".env.example"
    if not env.exists() and example.exists():
        shutil.copy(example, env)
        print(".env 생성됨 — OUTPUTS_DIR / MONGO_* 를 확인하세요.")


def cmd_serve(args: argparse.Namespace) -> None:
    _ensure_env()
    import uvicorn
    from settings import API_HOST, API_PORT, OUTPUTS_DIR, model_dir

    print(f"OUTPUTS_DIR={OUTPUTS_DIR}")
    for task in ("qa", "generation", "summary"):
        path = model_dir(task)
        mark = "OK" if path.exists() else "MISSING"
        print(f"  {task:12} {mark}  {path}")

    host = args.host or API_HOST
    port = args.port or API_PORT
    print(f"API http://{host if host != '0.0.0.0' else '127.0.0.1'}:{port}/docs")
    uvicorn.run("main:app", host=host, port=port, reload=args.reload)


def cmd_verify(_: argparse.Namespace) -> None:
    _ensure_env()
    from settings import OUTPUTS_DIR, model_dir

    print("=" * 50)
    print("Mission 5 검증 — Backend 모델 경로")
    print("=" * 50)
    print(f"OUTPUTS_DIR: {OUTPUTS_DIR}")
    ok = True
    for task in ("qa", "generation", "summary"):
        path = model_dir(task)
        if path.exists():
            print(f"  {task:12} OK  ({path})")
        else:
            print(f"  {task:12} MISSING  ({path})")
            ok = False
    print()
    if ok:
        print("MISSION 5 BACKEND PASSED ✓")
        raise SystemExit(0)
    print("MISSION 5 BACKEND FAILED")
    print("힌트: outputs/<task>/final 에 모델을 배치하세요.")
    raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Mission 5 Backend API")
    sub = parser.add_subparsers(dest="command", required=True)

    p_serve = sub.add_parser("serve", help="FastAPI 서버 실행")
    p_serve.add_argument("--host", default=None)
    p_serve.add_argument("--port", type=int, default=None)
    p_serve.add_argument("--reload", action="store_true")
    p_serve.set_defaults(func=cmd_serve)

    p_verify = sub.add_parser("verify", help="모델 경로 검증")
    p_verify.set_defaults(func=cmd_verify)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
