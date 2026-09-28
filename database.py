import sqlite3
import json
from datetime import datetime

DB_NAME = "fathul_qorib_v1.db"

def init_db():
    """Membuat tabel jika belum ada."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabel Pengguna Sederhana
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabel Perekaman Attempt (Analisis I'rab & Timer)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            sentence_id TEXT NOT NULL,
            phase1_duration_sec REAL,
            phase2_duration_sec REAL,
            score_percentage REAL,
            user_answers_json TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def save_attempt(username: str, sentence_id: str, p1_time: float, p2_time: float, score: float, answers: dict):
    """Menyimpan hasil pengerjaan analisis ke SQLite."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Pastikan user terdaftar
    cursor.execute("INSERT OR IGNORE INTO users (username) VALUES (?)", (username,))
    
    # Simpan attempt
    cursor.execute("""
        INSERT INTO attempts (username, sentence_id, phase1_duration_sec, phase2_duration_sec, score_percentage, user_answers_json)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (username, sentence_id, p1_time, p2_time, score, json.dumps(answers, ensure_ascii=False)))
    
    conn.commit()
    conn.close()

def get_user_history(username: str):
    """Mengambil riwayat pengerjaan user."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sentence_id, score_percentage, phase2_duration_sec, timestamp 
        FROM attempts WHERE username = ? ORDER BY id DESC
    """, (username,))
    rows = cursor.fetchall()
    conn.close()
    return rows
    
