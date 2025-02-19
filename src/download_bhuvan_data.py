import requests
import os

# Define API credentials and endpoint (use environment variables for security)
bhuvan_api_key = os.getenv('BHUVAN_API_KEY')
bhuvan_api_url = 'https://bhuvan.nrsc.gov.in/api/'

# Function to search and download Bhuvan data
def download_bhuvan_data(query, filename):
    search_url = f"{bhuvan_api_url}search?q={query}&key={bhuvan_api_key}"
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
    filename = os.path.join('data/bhuvan_images', 'sample_image.tif')
    download_bhuvan_data(query, filename)