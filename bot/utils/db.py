import sqlite3
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") or "upwork_bot.db"

async def create_db():
    """Creates the database and tables if they don't exist."""
    async def _create_db():
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                url TEXT,
                budget REAL,
                skills TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS proposals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT,
                cover_letter TEXT,
                status TEXT,
                FOREIGN KEY (job_id) REFERENCES jobs (id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proposal_id INTEGER,
                message TEXT,
                FOREIGN KEY (proposal_id) REFERENCES proposals (id)
            )
        """)

        conn.commit()
        conn.close()

    await asyncio.to_thread(_create_db)

def save_job(job):
    """Saves a job to the database."""
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO jobs (id, title, description, url, budget, skills)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (job.id, job.title, job.description, job.url, job.budget, ",".join(job.skills)))

    conn.commit()
    conn.close()

def save_proposal(job_id, cover_letter, status):
    """Saves a proposal to the database."""
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO proposals (job_id, cover_letter, status)
        VALUES (?, ?, ?)
    """, (job_id, cover_letter, status))

    conn.commit()
    conn.close()

def save_response(proposal_id, message):
    """Saves a response to the database."""
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO responses (proposal_id, message)
        VALUES (?, ?)
    """, (proposal_id, message))

    conn.commit()
    conn.close()

def get_job(job_id):
    """Gets a job from the database."""
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM jobs WHERE id = ?
    """, (job_id,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return Job(id=row[0], title=row[1], description=row[2], url=row[3], budget=row[4], skills=row[5].split(","))
    else:
        return None