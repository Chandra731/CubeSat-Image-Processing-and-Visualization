import requests
from models import session, CubeSat

def fetch_tle_data():
    url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=cubesat&FORMAT=tle"
    print("Fetching TLE data from:", url)  
    response = requests.get(url)
    tle_data = response.text
    print("Fetched TLE data successfully.")  

    print("Clearing existing CubeSat data from the database...")  
    session.query(CubeSat).delete()
    session.commit()
    print("Cleared existing CubeSat data.")  

    lines = tle_data.strip().split("\n")
    for i in range(0, len(lines), 3):
        satellite = lines[i].strip()
        line1 = lines[i + 1].strip()
        line2 = lines[i + 2].strip()
        print(f"Storing CubeSat: {satellite}")  
        new_entry = CubeSat(satellite=satellite, line1=line1, line2=line2)
        session.add(new_entry)

    session.commit()
    print("TLE data fetched and stored successfully.") 

if __name__ == "__main__":
    fetch_tle_data()