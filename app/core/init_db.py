from app.core.database import engine, Base
from app.models.country_info import Country_info
from app.core.logger import setup_logger

logger = setup_logger(__name__)

def init():
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Tables créées avec succès")

if __name__ == "__main__":
    init()