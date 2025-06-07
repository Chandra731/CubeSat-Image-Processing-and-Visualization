# Backend - CubeSat Onboard AI Image Classification and 3D Visualization

## Overview

This backend is a Flask REST API server that supports the CubeSat Visualization Platform by providing:

- CubeSat orbit and position data
- User authentication and session management
- Image upload and classification integration
- Image and classification history management
- TLE data updates from Celestrak
- Google Earth Engine integration for satellite image capture

---

## Technology Stack

- Python 3.x
- Flask, Flask-CORS, Flask-Mail
- SQLAlchemy ORM with SQLite (default)
- Google Earth Engine Python API
- SGP4 and Skyfield for satellite orbit calculations
- Requests for external HTTP calls

---

## Setup Instructions

1. Create a python virtual environment `python -m venv venv`.
2. Activate the virtual environment `source venv/bin/activate` (on Linux/Mac) or `.\venv\Scripts\activate` (on Windows).
3. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure environment variables as needed (e.g., `DATABASE_URL`, email SMTP credentials in `app.py`).

3. Initialize the database (tables are created automatically on first run).

4. Run the backend server:

```bash
python app.py
```

5. The API will be available at `http://127.0.0.1:5001`.

---

## API Endpoints

- **Authentication:**
  - `/auth/register` - Register new user
  - `/auth/login` - User login
  - `/auth/logout` - User logout
  - `/auth/password_reset_request` - Request password reset email
  - `/auth/password_reset/<token>` - Reset password

- **CubeSat Data:**
  - `/cubesat_orbits` - Get CubeSat orbit data
  - `/cubesat_positions` - Get current CubeSat positions
  - `/cubesat_chart_data` - Get altitude chart data
  - `/cubesat_heatmap_data` - Get heatmap data

- **Image Handling:**
  - `/upload_image` - Upload image
  - `/classify_image` - Classify image using AI model
  - `/image_history` - Get image history
  - `/classification_history` - Get classification history
  - `/delete_image/<id>` - Delete image or classification by ID

- **TLE Updates:**
  - `/update_tle` - Update TLE data from Celestrak

---

## Important Files

- `app.py` - Main Flask app and blueprint registration
- `models.py` - SQLAlchemy ORM models
- `routes/` - API route modules
- `database.py` - Database engine and session setup
- `utils.py` - Utility functions for DB session and error handling
- `fetch_tle.py` - Script to fetch and update TLE data
- `database_op.py` - CLI tool for database management

---

## Notes

- Default database is SQLite but can be configured via `DATABASE_URL`.
- Email credentials must be configured for password reset functionality.
- TLE data updates are rate-limited to once per 24 hours.
- Logging is enabled for debugging and error tracking.
