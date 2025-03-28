import requests
from sqlalchemy.orm import sessionmaker
from database import engine
from models import CubeSat

TLE_URL = "https://celestrak.org/NORAD/elements/gp.php?GROUP=cubesat&FORMAT=tle"

Session = sessionmaker(bind=engine)
session = Session()

def fetch_tle_data():
    response = requests.get(TLE_URL)
    if response.status_code == 200:
        tle_data = response.text.split("\n")
        for i in range(0, len(tle_data) - 2, 3):
            satellite = tle_data[i].strip()
            line1 = tle_data[i + 1].strip()
            line2 = tle_data[i + 2].strip()

            existing = session.query(CubeSat).filter_by(satellite=satellite).first()
            if existing:
                existing.line1 = line1
                existing.line2 = line2
            else:
                new_satellite = CubeSat(satellite=satellite, line1=line1, line2=line2)
                session.add(new_satellite)

        session.commit()
    else:
        print("Failed to fetch TLE data")

if __name__ == "__main__":
    fetch_tle_data()
