import sqlite3
import os
from flask import g, current_app

DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/student_subjects.db')

# Shared in-memory connection for testing
_memory_db = None


def get_db():
    if 'db' not in g:
        db_path = current_app.config.get('DATABASE_PATH', DATABASE_PATH)
        if db_path == ':memory:':
            global _memory_db
            if _memory_db is None:
                _memory_db = sqlite3.connect(':memory:')
                _memory_db.row_factory = sqlite3.Row
                _memory_db.execute("PRAGMA foreign_keys = ON")
            g.db = _memory_db
        else:
            db_dir = os.path.dirname(db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
            g.db = sqlite3.connect(db_path)
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
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
