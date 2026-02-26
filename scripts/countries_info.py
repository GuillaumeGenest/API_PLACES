import sys
import json
from pathlib import Path
from app.core.database import SessionLocal
from app.models.country_info import Country_info

SEEDS_PATH = Path("seeds/countries")


def upsert_country(data: dict, db):
    """Insère ou met à jour un pays — utilisé par toutes les fonctions"""
    country = db.query(Country_info).filter_by(
        country_code=data["country_code"].upper()
    ).first()

    if country:
        for key, value in data.items():
            if value is not None:
                setattr(country, key, value)
        print(f"🔄 {data['country_code']} - {data['name']} mis à jour")
    else:
        country = Country_info(**data)
        db.add(country)
        print(f"✅ {data['country_code']} - {data['name']} inséré")


def import_one(country_code: str):
    """Peuple ou met à jour un seul pays depuis son fichier JSON"""
    db = SessionLocal()
    try:
        file = SEEDS_PATH / f"{country_code.upper()}.json"
        if not file.exists():
            print(f"❌ Fichier {country_code.upper()}.json introuvable dans seeds/countries/")
            return
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        upsert_country(data, db)
        db.commit()
        print(f"🎉 Terminé")
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur : {e}")
    finally:
        db.close()


def import_all():
    """Peuple ou met à jour tous les pays depuis les fichiers JSON"""
    db = SessionLocal()
    try:
        files = list(SEEDS_PATH.glob("*.json"))
        if not files:
            print(f"❌ Aucun fichier JSON trouvé dans {SEEDS_PATH}")
            return
        print(f"📂 {len(files)} fichiers trouvés")
        for file in files:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
            upsert_country(data, db)
        db.commit()
        print(f"🎉 Import terminé")
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur : {e}")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m scripts.countries import_all")
        print("  python -m scripts.countries import_one JP")
        sys.exit(1)

    command = sys.argv[1]

    if command == "import_all":
        import_all()
    elif command == "import_one":
        if len(sys.argv) < 3:
            print("❌ Précise le code pays. Ex: python -m scripts.countries import_one JP")
            sys.exit(1)
        import_one(sys.argv[2])
    else:
        print(f"❌ Commande inconnue : {command}")