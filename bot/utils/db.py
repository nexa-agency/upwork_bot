import sqlite3
import os
import asyncio
from dotenv import load_dotenv
from datetime import datetime
from utils.db import create_db

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") or "upwork_bot.db"

asyncio.run(create_db())


def save_job(job):
    """Saves a job to the database."""
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO jobs (id, title, description, url, budget, skills)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (job.id, job.title, job.description, job.url, job.budget, ",".join(job.skills)),
    )

    conn.commit()
    conn.close()


def save_proposal(job_id, cover_letter, status):
    """Saves a proposal to the database."""
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO proposals (job_id, cover_letter, status)
        VALUES (?, ?, ?)
    """,
        (job_id, cover_letter, status),
    )

    conn.commit()
    conn.close()


def save_response(proposal_id, message):
    """Saves a response to the database."""
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO responses (proposal_id, message)
        VALUES (?, ?)
    """,
        (proposal_id, message),
    )

    conn.commit()
    conn.close()


def get_job(job_id):
    """Gets a job from the database."""
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM jobs WHERE id = ?
    """,
        (job_id,),
    )

    row = cursor.fetchone()
    conn.close()

    if row:
        return Job(
            id=row[0],
            title=row[1],
            description=row[2],
            url=row[3],
            budget=row[4],
            skills=row[5].split(","),
        )
    else:
        return None


def save_post(text, image_url):
    """Saves a generated post to the database."""
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO posts (text, image_url, created_at)
        VALUES (?, ?, ?)
    """,
        (text, image_url, datetime.utcnow().isoformat()),
    )

    conn.commit()
    conn.close()


def get_last_post():
    """Gets the last generated post from the database."""
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT text, image_url, created_at FROM posts
        ORDER BY created_at DESC
        LIMIT 1
    """
    )

    row = cursor.fetchone()
    conn.close()

    if row:
        return {"text": row[0], "image_url": row[1], "created_at": row[2]}
    else:
        return None
