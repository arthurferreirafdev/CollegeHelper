import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DATABASE_URL = os.getenv('DATABASE_URL')
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/student_subjects.db')
    API_HOST = os.getenv('API_HOST', 'localhost')
    API_PORT = int(os.getenv('API_PORT', 5000))
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
