import sqlite3
import os
from flask import g, current_app

DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/student_subjects.db')

# Shared in-memory connection for testing
_memory_db = None


import psycopg2
from flask import g, current_app

import psycopg
from flask import g, current_app

def get_db():
    if "db" not in g:
        g.db = psycopg.connect(
            conninfo=current_app.config["DATABASE_URL"],
            row_factory=psycopg.rows.dict_row  # retorna resultados como dicionário
        )
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None and db is not _memory_db:
        db.close()


def init_db(app):
    with app.app_context():
        db = get_db()
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r') as f:
            db.executescript(f.read())
        db.commit()
