import sys
import json
from pathlib import Path
from app.core.database import SessionLocal
from app.models.country_info import Country_info
from app.core.logger import setup_logger
logger = setup_logger(__name__)

SEEDS_PATH = Path("seeds/countries")


def upsert_country(data: dict, db):
    """Insère ou met à jour un pays"""
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
    """Import un pays via son code"""
    logger.info("DB | debut import one")

    db = SessionLocal()
    try:
        file = next(SEEDS_PATH.rglob(f"{country_code.upper()}.json"), None)

        if not file:
            logger.error(f"❌ Fichier {country_code.upper()} introuvable")
            return
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        upsert_country(data, db)
        db.commit()
        logger.info("🎉 Import country terminé")

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erreur import_one : {e}")

    finally:
        db.close()


def import_all():
    """Import tous les pays (tous continents)"""
    logger.info("DB | debut import all")

    db = SessionLocal()
    try:
        files = list(SEEDS_PATH.rglob("*.json"))

        if not files:
            print("❌ Aucun fichier JSON trouvé")
            return
        print(f"📂 {len(files)} fichiers trouvés")
        for file in files:
            try:
                print(f"📄 {file.relative_to(SEEDS_PATH)}")
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                upsert_country(data, db)
                logger.info(
                    f"DB | import {data['country_code']} - {data['name']}"
                )

            except Exception as e:
                logger.error(f"❌ ERREUR fichier {file.name} : {e}")
                raise

        db.commit()
        print("🎉 Import ALL terminé")

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erreur import_all : {e}")

    finally:
        db.close()


def import_continent(continent: str):
    """Import tous les pays d'un continent"""
    logger.info(f"DB | import continent {continent}")

    db = SessionLocal()

    try:
        base_path = SEEDS_PATH / continent

        if not base_path.exists():
            logger.error(f"❌ Continent introuvable : {continent}")
            return

        files = list(base_path.rglob("*.json"))

        if not files:
            logger.error(f"❌ Aucun fichier dans {continent}")
            return

        print(f"📂 {len(files)} fichiers dans {continent}")

        for file in files:
            try:
                print(f"📄 {continent}/{file.name}")

                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                upsert_country(data, db)
                logger.info(
                    f"DB | {continent} | {data['country_code']} - {data['name']}"
                )

            except Exception as e:
                logger.error(f"❌ ERREUR {file.name} : {e}")
                raise

        db.commit()
        print(f"🎉 Import continent {continent} terminé")

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erreur continent {continent} : {e}")

    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  import_all")
        print("  import_one IE")
        print("  import_continent Europe")
        sys.exit(1)

    command = sys.argv[1]

    if command == "import_all":
        import_all()

    elif command == "import_one":
        if len(sys.argv) < 3:
            print("❌ country code manquant")
            sys.exit(1)
        import_one(sys.argv[2])

    elif command == "import_continent":
        if len(sys.argv) < 3:
            print("❌ continent manquant")
            sys.exit(1)
        import_continent(sys.argv[2])

    else:
        print(f"❌ commande inconnue : {command}")