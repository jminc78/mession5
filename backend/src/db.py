"""미션 1 MongoDB에서 소설 목록을 조회합니다."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

from pymongo import MongoClient
from pymongo.database import Database

from settings import get_database_url, get_db_name, load_dotenv


@contextmanager
def connect() -> Iterator[Database]:
    load_dotenv()
    client = MongoClient(get_database_url())
    try:
        yield client[get_db_name()]
    finally:
        client.close()


def fetch_novels() -> list[dict[str, Any]]:
    with connect() as db:
        rows = list(
            db.novels.find(
                {},
                {
                    "_id": 0,
                    "file_stem": 1,
                    "title": 1,
                    "author": 1,
                    "content": 1,
                    "char_count": 1,
                },
            ).sort("title", 1)
        )
    return rows
