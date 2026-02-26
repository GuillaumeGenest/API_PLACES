from fastapi import APIRouter, HTTPException
from app.services.country_info_service import get_all_countries, get_country_by_code, search_countries

router = APIRouter(prefix="/country_info", tags=["country_info"])

@router.get("/")
def list_countries():
    countries = get_all_countries()
    if not countries:
        raise HTTPException(status_code=404, detail="Aucun pays trouvé")
    return countries

@router.get("/search")
def search(query: str):
    countries = search_countries(query)
    if not countries:
        raise HTTPException(status_code=404, detail=f"Aucun pays trouvé pour : {query}")
    return countries

@router.get("/{country_code}")
def get_country(country_code: str):
    country = get_country_by_code(country_code)
    if not country:
        raise HTTPException(status_code=404, detail=f"Pays introuvable : {country_code}")
    return country