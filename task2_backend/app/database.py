import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# =================================
# Load .env safely
# =================================
# Try loading from the current app directory, then parent
current_dir = os.path.dirname(os.path.abspath(__file__))
env_paths = [
    os.path.join(current_dir, ".env"),
    os.path.join(current_dir, "..", ".env"),
    os.path.abspath(os.path.join(current_dir, "..", "..", ".env"))
]

for path in env_paths:
    if os.path.exists(path):
        load_dotenv(path)

# =================================
# Use DATABASE_URL from environment
# =================================
DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback path for local development
SQLITE_URL = "sqlite:///./reviews.db"

if not DATABASE_URL:
    DATABASE_URL = SQLITE_URL

# SQLAlchemy 1.4+ requires 'postgresql+psycopg2://' instead of 'postgresql://'
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# Create SQLAlchemy engine
# pool_pre_ping is important for Postgres on Render/managed services
try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
    )
    # Test connection
    with engine.connect() as conn:
        pass
except Exception as e:
    print(f"WARNING: Could not connect to primary DATABASE_URL. Falling back to SQLite. Error: {e}")
    DATABASE_URL = SQLITE_URL
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
    )

# Create session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base model
Base = declarative_base()
