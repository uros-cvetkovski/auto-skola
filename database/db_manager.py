import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "auto_skola.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS kandidati (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ime TEXT NOT NULL,
            prezime TEXT NOT NULL,
            jmbg TEXT UNIQUE NOT NULL,
            telefon TEXT,
            email TEXT,
            datum_upisa TEXT,
            status TEXT DEFAULT 'aktivan'
        );

        CREATE TABLE IF NOT EXISTS instruktori (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ime TEXT NOT NULL,
            prezime TEXT NOT NULL,
            telefon TEXT,
            kategorija TEXT DEFAULT 'B',
            aktivan INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS casovi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kandidat_id INTEGER REFERENCES kandidati(id),
            instruktor_id INTEGER REFERENCES instruktori(id),
            datum TEXT,
            vreme TEXT,
            status TEXT DEFAULT 'zakazan',
            napomena TEXT
        );

        CREATE TABLE IF NOT EXISTS ispiti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kandidat_id INTEGER REFERENCES kandidati(id),
            tip TEXT,
            datum TEXT,
            rezultat TEXT DEFAULT 'ceka',
            napomena TEXT
        );
    """)

    conn.commit()
    conn.close()