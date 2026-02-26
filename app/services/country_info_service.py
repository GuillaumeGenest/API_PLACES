from app.core.database import SessionLocal
from app.models.country_info import Country_info

def get_all_countries():
    db = SessionLocal()
    try:
        countries = db.query(Country_info).order_by(Country_info.name).all()
        return countries
    except Exception as e:
        print(f"Erreur get_all_countries: {e}")
        return None
    finally:
        db.close()

def get_country_by_code(country_code: str):
    db = SessionLocal()
    try:
        country = db.query(Country_info).filter(
            Country_info.country_code == country_code.upper()
        ).first()
        return country
    except Exception as e:
        print(f"Erreur get_country_by_code: {e}")
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
        print(f"Erreur search_countries: {e}")
        return None
    finally:
        db.close()