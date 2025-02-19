import requests
import os

# Define API credentials and endpoint (use environment variables for security)
nasa_earthdata_username = os.getenv('NASA_EARTHDATA_USERNAME')
nasa_earthdata_password = os.getenv('NASA_EARTHDATA_PASSWORD')
nasa_earthdata_api_url = 'https://earthdata.nasa.gov/api/'

# Function to search and download NASA Earthdata
def download_nasa_earthdata(query, filename):
    search_url = f"{nasa_earthdata_api_url}search?q={query}"
    response = requests.get(search_url, auth=(nasa_earthdata_username, nasa_earthdata_password))
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded data to {filename}")
    else:
        print(f"Failed to download data: {response.status_code}")

# Example usage
if __name__ == "__main__":
    query = 'sample_query'
    filename = os.path.join('data/nasa_earthdata_images', 'sample_image.tif')
    download_nasa_earthdata(query, filename)