from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./data/visitors.db"

engine = create_engine(DATABASE_URL,
                       connect_args={"check_same_thread": False})

SessionLoacl = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLoacl()
    try:
        yield db
    finally:
        db.close()

