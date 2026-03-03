from fastapi import APIRouter, HTTPException
from app.services.country_info_service import get_all_countries, get_country_by_code, search_countries
from app.core.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/country_info", tags=["country_info"])

@router.get("/")
def list_countries():
    logger.info("HTTP | GET /country_info — liste tous les pays")
    countries = get_all_countries()
    if not countries:
        logger.warning("HTTP | GET /country_info — aucun pays trouvé")
        raise HTTPException(status_code=404, detail="Aucun pays trouvé")
    logger.info(f"HTTP | GET /country_info — succès {len(countries)} pays retournés")
    return countries

@router.get("/search")
def search(query: str):
    logger.info(f"HTTP | GET /country_info/search — query={query}")
    countries = search_countries(query)
    if not countries:
        logger.warning(f"HTTP | GET /country_info/search — aucun résultat query={query}")
        raise HTTPException(status_code=404, detail=f"Aucun pays trouvé pour : {query}")
    logger.info(f"HTTP | GET /country_info/search — succès {len(countries)} résultats query={query}")
    return countries

@router.get("/{country_code}")
def get_country(country_code: str):
    logger.info(f"HTTP | GET /country_info/{country_code}")
    country = get_country_by_code(country_code)
    if not country:
        logger.warning(f"HTTP | GET /country_info/{country_code} — pays introuvable")
        raise HTTPException(status_code=404, detail=f"Pays introuvable : {country_code}")
    logger.info(f"HTTP | GET /country_info/{country_code} — succès")
    return country