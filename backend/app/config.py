"""
Configuration management.
Load configuration uniformly from the project root `.env` file.
"""

import os
from dotenv import load_dotenv

# Load the `.env` file from the project root.
# Path: project-root/.env (relative to `backend/app/config.py`)
project_root_env = os.path.join(os.path.dirname(__file__), '../../.env')

if os.path.exists(project_root_env):
    load_dotenv(project_root_env, override=True)
else:
    # If the root directory has no `.env`, try loading environment variables directly.
    load_dotenv(override=True)


class Config:
    """Flask configuration class."""
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ops-secret-key')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    AUTH_REQUIRED = os.environ.get(
        'AUTH_REQUIRED',
        'false' if DEBUG else 'true'
    ).lower() == 'true'
    FRONTEND_ORIGIN = os.environ.get('FRONTEND_ORIGIN', '').strip()
    FRONTEND_ORIGINS = [
        value.strip()
        for value in os.environ.get('FRONTEND_ORIGINS', '').split(',')
        if value.strip()
    ]
    
    # JSON configuration: disable ASCII escaping so non-ASCII text is shown directly.
    JSON_AS_ASCII = False
    
    # LLM configuration (use the OpenAI-compatible format throughout)
    LLM_API_KEY = os.environ.get('LLM_API_KEY', 'ollama')
    LLM_BASE_URL = os.environ.get('LLM_BASE_URL', 'http://localhost:11434/v1')
    LLM_MODEL_NAME = os.environ.get('LLM_MODEL_NAME', 'qwen2.5:7b')

    # Three-tier LLM model routing (falls back to LLM_MODEL_NAME if not set)
    # Persona generation — needs creativity and cultural depth
    LLM_PERSONA_MODEL = os.environ.get('LLM_PERSONA_MODEL', LLM_MODEL_NAME)
    # Simulation runtime — needs speed, runs per-agent per-round
    LLM_SIMULATION_MODEL = os.environ.get('LLM_SIMULATION_MODEL', LLM_MODEL_NAME)
    # Report generation — needs analytical depth
    LLM_REPORT_MODEL = os.environ.get('LLM_REPORT_MODEL', LLM_MODEL_NAME)

    # Boost LLM (heavier tasks — config generation, complex analysis)
    LLM_BOOST_API_KEY = os.environ.get('LLM_BOOST_API_KEY', LLM_API_KEY)
    LLM_BOOST_BASE_URL = os.environ.get('LLM_BOOST_BASE_URL', LLM_BASE_URL)
    LLM_BOOST_MODEL_NAME = os.environ.get('LLM_BOOST_MODEL_NAME', LLM_MODEL_NAME)
    
    # Zep configuration
    ZEP_API_KEY = os.environ.get('ZEP_API_KEY')
    ZEP_ENABLED = bool(ZEP_API_KEY)

    # Supabase OPS temporal-memory configuration
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
    OPS_MEMORY_STORE_ENABLED = bool(SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY)
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    UPLOAD_FOLDER = os.path.abspath(
        os.environ.get(
            'UPLOAD_FOLDER',
            os.path.join(os.path.dirname(__file__), '../uploads'),
        )
    )
    ALLOWED_EXTENSIONS = {'pdf', 'md', 'txt', 'markdown'}
    
    # Text processing configuration
    DEFAULT_CHUNK_SIZE = 500  # Default chunk size
    DEFAULT_CHUNK_OVERLAP = 50  # Default overlap size
    
    # OASIS simulation configuration
    OASIS_DEFAULT_MAX_ROUNDS = int(os.environ.get('OASIS_DEFAULT_MAX_ROUNDS', '10'))
    OASIS_SIMULATION_DATA_DIR = os.path.abspath(
        os.environ.get(
            'OASIS_SIMULATION_DATA_DIR',
            os.path.join(UPLOAD_FOLDER, 'simulations'),
        )
    )
    
    # OASIS platform action configuration
    OASIS_TWITTER_ACTIONS = [
        'CREATE_POST', 'LIKE_POST', 'REPOST', 'FOLLOW', 'DO_NOTHING', 'QUOTE_POST'
    ]
    OASIS_REDDIT_ACTIONS = [
        'LIKE_POST', 'DISLIKE_POST', 'CREATE_POST', 'CREATE_COMMENT',
        'LIKE_COMMENT', 'DISLIKE_COMMENT', 'SEARCH_POSTS', 'SEARCH_USER',
        'TREND', 'REFRESH', 'DO_NOTHING', 'FOLLOW', 'MUTE'
    ]
    
    # Report Agent configuration
    REPORT_AGENT_MAX_TOOL_CALLS = int(os.environ.get('REPORT_AGENT_MAX_TOOL_CALLS', '5'))
    REPORT_AGENT_MAX_REFLECTION_ROUNDS = int(os.environ.get('REPORT_AGENT_MAX_REFLECTION_ROUNDS', '2'))
    REPORT_AGENT_TEMPERATURE = float(os.environ.get('REPORT_AGENT_TEMPERATURE', '0.5'))

    @classmethod
    def get_cors_origins(cls):
        """Return configured frontend origins for CORS."""
        origins = []
        if cls.FRONTEND_ORIGIN:
            origins.append(cls.FRONTEND_ORIGIN)
        origins.extend(origin for origin in cls.FRONTEND_ORIGINS if origin not in origins)
        return origins
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        errors = []
        if not cls.LLM_API_KEY:
            errors.append("LLM_API_KEY is not configured")
        if cls.AUTH_REQUIRED and not (cls.SUPABASE_URL and cls.SUPABASE_SERVICE_ROLE_KEY):
            errors.append("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be configured when AUTH_REQUIRED is enabled")
        if not cls.DEBUG:
            if cls.SECRET_KEY == 'ops-secret-key':
                errors.append("SECRET_KEY must be set to a non-default value in production")
            if not cls.get_cors_origins():
                errors.append("FRONTEND_ORIGIN or FRONTEND_ORIGINS must be configured in production")
        return errors
