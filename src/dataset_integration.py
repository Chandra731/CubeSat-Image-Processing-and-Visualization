import os
import shutil

# Define dataset directories
bhuvan_dir = 'data/bhuvan_images/'
mosdac_dir = 'data/mosdac_images/'
nasa_dir = 'data/nasa_earthdata_images/'
integrated_dir = 'data/integrated_images/'

# Ensure the integrated directory exists
os.makedirs(integrated_dir, exist_ok=True)

# Function to copy images from source to destination
def copy_images(src_dir, dest_dir):
    for filename in os.listdir(src_dir):
        full_file_name = os.path.join(src_dir, filename)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, dest_dir)

# Copy images from each dataset directory to the integrated directory
copy_images(bhuvan_dir, integrated_dir)
copy_images(mosdac_dir, integrated_dir)
copy_images(nasa_dir, integrated_dir)

print("Dataset integration completed.")