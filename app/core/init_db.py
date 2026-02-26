from app.core.database import engine, Base
from app.models.country_info import Country_info

def init():
    Base.metadata.create_all(bind=engine)
    print("✅ Tables créées avec succès")

if __name__ == "__main__":
    init()