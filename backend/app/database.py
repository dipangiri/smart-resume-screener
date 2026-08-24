import sqlite3
from pathlib import Path
from typing import Iterable

from app.config import get_settings


def _database_path() -> Path:
    url = get_settings().database_url
    if not url.startswith("sqlite:///"):
        raise ValueError("Only sqlite:/// DATABASE_URL values are supported.")

    path = Path(url.replace("sqlite:///", "", 1))
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[1] / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(_database_path())
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                name TEXT,
                email TEXT,
                phone TEXT,
                skills TEXT NOT NULL DEFAULT '[]',
                experience TEXT,
                education TEXT,
                raw_text TEXT NOT NULL,
                score REAL,
                verdict TEXT,
                justification TEXT,
                strengths TEXT NOT NULL DEFAULT '[]',
                gaps TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS screening_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_description TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def insert_candidate(candidate: dict) -> int:
    keys = ", ".join(candidate.keys())
    placeholders = ", ".join("?" for _ in candidate)
    values = list(candidate.values())

    with get_connection() as conn:
        cursor = conn.execute(
            f"INSERT INTO candidates ({keys}) VALUES ({placeholders})",
            values,
        )
        return int(cursor.lastrowid)


def insert_screening_run(job_description: str) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO screening_runs (job_description) VALUES (?)",
            (job_description,),
        )
        return int(cursor.lastrowid)


def list_candidates() -> Iterable[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT id, filename, name, email, phone, skills, experience, education,
                   score, verdict, justification, strengths, gaps, created_at
            FROM candidates
            ORDER BY created_at DESC
            """
        ).fetchall()

