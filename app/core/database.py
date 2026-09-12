from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()
_engine = None
_SessionLocal = None

def get_engine():
    global _engine
    if _engine is None:
        from app.core.config import get_database_url
        _engine = create_engine(get_database_url())
        logger.info("DB | Engine créé")
    return _engine

def SessionLocal():
    global _SessionLocal
    if _SessionLocal is None:
        Session = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
        _SessionLocal = Session
    return _SessionLocal()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    try:
        with get_engine().connect() as conn:
            logger.info("✅ Connexion à la base de données OK")
    except Exception as e:
        logger.error(f"❌ Erreur de connexion : {e}")