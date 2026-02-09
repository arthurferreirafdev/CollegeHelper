"""
CONFIGURATION MODULE
===================
This module handles all configuration settings for the student subject
selection system. It manages environment variables, database paths,
API keys, and other system settings.

Features:
- Environment-based configuration
- Default values for development
- Validation of required settings
- Easy configuration management

Usage:
    from config import Config
    config = Config()
    db_path = config.DATABASE_PATH
"""

import os
from typing import Optional

class Config:
    """
    Configuration management class for the student subject selection system.
    Handles all environment variables and system settings.
    """
    
    def __init__(self):
        """
        Initialize configuration with environment variables and defaults.
        """
        # Load environment variables from .env file if available
        self._load_env_file()
        
        # Database configuration
        self.DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/student_subjects.db')
        
        # API server configuration
        self.API_HOST = os.getenv('API_HOST', 'localhost')
        self.API_PORT = int(os.getenv('API_PORT', 5000))
        self.FLASK_ENV = os.getenv('FLASK_ENV', 'development')
        
        # Security configuration
        self.SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
        self.JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
        
        # OpenAI configuration
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        
        # Frontend configuration
        self.FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        
        # Email configuration (for future features)
        self.SMTP_SERVER = os.getenv('SMTP_SERVER')
        self.SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
        self.SMTP_USERNAME = os.getenv('SMTP_USERNAME')
        self.SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
        
        # Validate critical configuration
        self._validate_config()
    
    def _load_env_file(self):
        """
        Load environment variables from .env file if it exists.
        """
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            # python-dotenv not installed, skip loading .env file
            pass
    
    def _validate_config(self):
        """
        Validate that all required configuration is present.
        """
        # Check for production security keys
        if self.FLASK_ENV == 'production':
            if self.SECRET_KEY == 'dev-secret-key-change-in-production':
                raise ValueError("SECRET_KEY must be set for production environment")
            
            if self.JWT_SECRET_KEY == 'jwt-secret-key-change-in-production':
                raise ValueError("JWT_SECRET_KEY must be set for production environment")
    
    def is_development(self) -> bool:
        """
        Check if running in development mode.
        
        Returns:
            bool: True if in development mode
        """
        return self.FLASK_ENV == 'development'
    
    def is_production(self) -> bool:
        """
        Check if running in production mode.
        
        Returns:
            bool: True if in production mode
        """
        return self.FLASK_ENV == 'production'
    
    def has_openai_key(self) -> bool:
        """
        Check if OpenAI API key is configured.
        
        Returns:
            bool: True if OpenAI key is available
        """
        return bool(self.OPENAI_API_KEY)
    
    def get_database_url(self) -> str:
        """
        Get the complete database URL/path.
        
        Returns:
            str: Database path or URL
        """
        return self.DATABASE_PATH
    
    def get_cors_origins(self) -> list:
        """
        Get allowed CORS origins for the API.
        
        Returns:
            list: List of allowed origins
        """
        if self.is_development():
            return [self.FRONTEND_URL, "http://localhost:3000", "http://127.0.0.1:3000"]
        else:
            return [self.FRONTEND_URL]
    
    def to_dict(self) -> dict:
        """
        Convert configuration to dictionary (excluding sensitive data).
        
        Returns:
            dict: Configuration dictionary
        """
        return {
            'database_path': self.DATABASE_PATH,
            'api_host': self.API_HOST,
            'api_port': self.API_PORT,
            'flask_env': self.FLASK_ENV,
            'frontend_url': self.FRONTEND_URL,
            'has_openai_key': self.has_openai_key(),
            'is_development': self.is_development(),
            'is_production': self.is_production()
        }

# Create a global configuration instance
config = Config()

# Example usage and configuration display
if __name__ == "__main__":
    print("⚙️  Student Subject Selection System Configuration")
    print("=" * 50)
    
    config_dict = config.to_dict()
    for key, value in config_dict.items():
        print(f"{key.upper()}: {value}")
    
    print("\n🔧 Configuration Status:")
    print(f"✅ Database Path: {config.DATABASE_PATH}")
    print(f"{'✅' if config.has_openai_key() else '❌'} OpenAI API Key: {'Configured' if config.has_openai_key() else 'Not configured'}")
    print(f"🌍 Environment: {config.FLASK_ENV}")
    print(f"🚀 API Server: {config.API_HOST}:{config.API_PORT}")
