import ee
import os

# Initialize the Earth Engine module.
ee.Initialize()

# Function to process data with Google Earth Engine
def process_data_with_gee():
    # Define a region of interest
    region = ee.Geometry.Rectangle([73.0, 20.0, 74.0, 21.0])

    # Load a Landsat 8 image collection
    collection = ee.ImageCollection('LANDSAT/LC08/C01/T1_TOA') \
        .filterDate('2020-01-01', '2020-12-31') \
        .filterBounds(region)

    # Compute the median of the collection
    median_image = collection.median()

    # Export the image to Google Drive
    task = ee.batch.Export.image.toDrive(**{
        'image': median_image,
        'description': 'Median_Image',
        'folder': 'EarthEngineImages',
        'region': region,
        'scale': 30
    })
    task.start()

# Example usage
if __name__ == "__main__":
    process_data_with_gee()
    print("Started Google Earth Engine processing task.")