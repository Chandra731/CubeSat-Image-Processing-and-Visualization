# Frontend - CubeSat Visualization Platform

This directory contains the frontend web application for the CubeSat Visualization Platform, built using Flask and modern JavaScript libraries.

---

## Overview

The frontend provides an interactive web interface for users to:

- Visualize CubeSat orbits and positions on a 3D globe using CesiumJS.
- Capture satellite images from Google Earth Engine datasets.
- Upload images for classification.
- View classification results and image history.
- Manage user authentication including login, registration, password reset, and logout.

---

## Technologies Used

- **Flask:** Serves HTML templates and static assets.
- **CesiumJS:** 3D globe visualization of satellite orbits and positions.
- **Leaflet & Heatmap.js:** Heatmap visualization of CubeSat positional density.
- **Chart.js:** Visualization of CubeSat altitude and velocity data.
- **Bootstrap 5:** Responsive UI styling and components.
- **JavaScript Modules:** Organized client-side logic for authentication, API communication, visualization, and UI interactions.

---

## Directory Structure

- `app.py`  
  Flask application entry point serving routes and static files.

- `templates/`  
  HTML templates for pages including:
  - `index.html` - Home page.
  - `visualization.html` - Main CubeSat visualization page.
  - `history.html` - Image and classification history.
  - `auth.html` - Authentication disabled notice.
  - `login.html`, `register.html`, `forgot_password.html`, `password_reset.html` - Authentication pages.

- `static/js/`  
  JavaScript modules:
  - `authHandler.js` - Handles user authentication flows and validation.
  - `apiHandler.js` - API request wrappers and UI update helpers.
  - `cesiumSetup.js` - Initializes Cesium viewer and satellite entities.
  - `charts.js` - Creates altitude and velocity charts using Chart.js.
  - `heatmap.js` - Creates heatmap visualization using Leaflet and heatmap.js.
  - `main.js` - Main frontend logic including event handlers and data fetching.
  - `uiHandler.js` - UI event listeners for logout and image history modal.

- `static/css/styles.css`  
  Custom CSS styles for the frontend.

---

## Setup and Running

1. **Prerequisites:**
   - Backend API server running (default: http://127.0.0.1:5001).
   - Python 3.x installed.
   - Create a python virtual environment `python -m venv venv`.
   - Activate the virtual environment `source venv/bin/activate` (on Linux/Mac) or `.\venv\Scripts\activate` (on Windows).
2. **Install dependencies:**
   - Install Flask and other Python dependencies if not already installed.

3. **Run the frontend server:**

```bash
cd frontend
python app.py
```

4. **Access the frontend:**
   - Open a browser and navigate to http://127.0.0.1:5000.

---

## Usage Details

- **Authentication:**
  - Users can register, login, request password reset, and reset passwords.
  - Authentication state is managed via cookies and session.
  - Navbar updates dynamically based on login status.

- **Visualization:**
  - CesiumJS displays CubeSat orbits and current positions with interactive labels.
  - Heatmap shows satellite positional density on a Leaflet map.
  - Charts display altitude and velocity data over time.

- **Image Capture and Classification:**
  - Users can capture satellite images by specifying latitude, longitude, and dataset.
  - Uploaded images can be classified using the AI model.
  - Classification results are displayed with confidence percentages.

- **History:**
  - Image and classification history can be viewed in modals.
  - Users can filter images by latitude and longitude.
  - Images and classifications can be deleted or downloaded.

---

## Notes

- The frontend relies heavily on asynchronous API calls to the backend.
- Client-side validation and user feedback are implemented for better UX.
- Cesium Ion access token is embedded in `cesiumSetup.js`.
- The frontend is designed to be responsive and user-friendly.
