import requests
import os

# Define API credentials and endpoint (use environment variables for security)
mosdac_api_key = os.getenv('MOSDAC_API_KEY')
mosdac_api_url = 'https://mosdac.gov.in/api/'

# Function to search and download MOSDAC data
def download_mosdac_data(query, filename):
    search_url = f"{mosdac_api_url}search?q={query}&key={mosdac_api_key}"
    response = requests.get(search_url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded data to {filename}")
    else:
        print(f"Failed to download data: {response.status_code}")

# Example usage
if __name__ == "__main__":
    query = 'sample_query'
    filename = os.path.join('data/mosdac_images', 'sample_image.tif')
    download_mosdac_data(query, filename)