from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, LargeBinary, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os

# Database URL (use SQLite for simplicity)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./senpai.db") # Default to SQLite

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}) # Remove check for SQLite

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Define database models
class AgentSession(Base):
    __tablename__ = "agent_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    task_description = Column(String)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    is_running = Column(Boolean, default=True)
    current_step = Column(Integer, nullable=True) # Add current step
    last_action = Column(String, nullable=True) # last Action
    last_selector = Column(String, nullable=True) # last Selector


class LogEntry(Base):
    __tablename__ = "log_entries"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    level = Column(String, default = 'INFO') #Log Level
    message = Column(String)
    dom = Column(Text, nullable = True)
    screenshot = Column(LargeBinary, nullable = True)

# Create the tables
Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
