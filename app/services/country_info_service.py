from app.core.database import SessionLocal
from app.models.country_info import Country_info
from app.core.logger import setup_logger
logger = setup_logger(__name__)

def get_all_countries():
    logger.info("DB | Récupération de tous les pays")
    db = SessionLocal()
    try:
        countries = db.query(Country_info).order_by(Country_info.name).all()
        logger.info(f"DB | {len(countries)} pays retournés")
        return countries
    except Exception as e:
        logger.error(f"DB | Erreur get_all_countries: {e}")
        return None
    finally:
        db.close()

def get_country_by_code(country_code: str):
    logger.info(f"DB | Recherche pays : {country_code}")
    db = SessionLocal()
    try:
        country = db.query(Country_info).filter(
            Country_info.country_code == country_code.upper()
        ).first()
        return country
    except Exception as e:
        logger.error(f"DB | Erreur get_all_countries: {e}")
        return None
    finally:
        db.close()

def search_countries(query: str):
    db = SessionLocal()
    try:
        countries = db.query(Country_info).filter(
            Country_info.name.ilike(f"%{query}%")
        ).order_by(Country_info.name).all()
        return countries
    except Exception as e:
        logger.error(f"DB | Erreur search_countries: {e}")
        return None
    finally:
        db.close()