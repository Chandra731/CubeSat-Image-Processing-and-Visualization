# CubeSat Visualization Project - File Functionality

## Backend Files

### `backend/models.py`
- Defines SQLAlchemy database models:
  - `CubeSat`: Stores satellite TLE data and computes positions using SGP4
  - `ImageHistory`: Tracks captured images with coordinates
  - `Classification`: Stores image classification results
- Includes position computation and serialization methods

### `backend/database.py`
- Configures database connection using SQLAlchemy
- Creates `Base` class for model inheritance
- Initializes database schema via `init_db()`
- Supports SQLite (default) and other databases via environment variable

### `backend/app.py`
- Main Flask application entry point
- Registers blueprints from route files
- Configures CORS for frontend-backend communication
- Initializes database connection

### Route Files
#### `backend/routes/cubesat.py`
- API endpoints for CubeSat data:
  - `/positions`: Returns current satellite positions
  - `/orbits`: Provides historical orbit data
  - `/update`: Endpoint for TLE updates

#### `backend/routes/classify.py`
- Handles image classification requests
- Processes uploaded images through AI model
- Returns classification results with confidence scores

#### `backend/routes/history.py`
- Manages image history operations:
  - `/history`: Retrieves stored images
  - `/store`: Saves new images
  - `/delete`: Removes images from history

### `backend/fetch_tle.py`
- Scheduled task to fetch fresh TLE data
- Updates satellite orbital elements
- Ensures position calculation accuracy

## Frontend Files

### `frontend/app.py`
- Serves static files and templates
- Defines routes for:
  - Main page (`/`)
  - History page (`/history`)
  - Static assets (JS, CSS, images)

### JavaScript Files
#### `frontend/static/js/cesiumSetup.js`
- Initializes Cesium 3D globe
- Configures terrain and visualization settings
- Sets up mouse interaction handlers
- Loads initial satellite data

#### `frontend/static/js/apiHandler.js`
- Manages all API communications:
  - `fetchCubeSatData()`: Gets satellite positions
  - `captureImage()`: Requests image capture
  - `fetchImageHistory()`: Retrieves stored images
  - Error handling and data validation

#### `frontend/static/js/uiHandler.js`
- Handles user interactions:
  - Coordinate display on mouse move
  - Image capture button logic
  - History navigation with state preservation
  - Image display and deletion

#### `frontend/static/js/main.js`
- Main application orchestrator:
  - Initializes Cesium viewer
  - Sets up UI event handlers
  - Coordinates data fetching
  - Manages chart and heatmap displays

### Template Files
#### `frontend/templates/index.html`
- Main application interface
- Contains Cesium container
- UI controls for interaction
- Image display area

#### `frontend/templates/history.html`
- Image history viewing interface
- Displays captured images
- Provides deletion functionality

## AI Model Files

### `ai_model/api.py`
- Exposes model as REST API
- Handles image classification requests
- Returns structured results

### `ai_model/infer.py`
- Contains model inference logic
- Loads trained model
- Processes input images
- Generates predictions

### `ai_model/preprocess.py`
- Image preprocessing utilities:
  - Normalization
  - Resizing
  - Format conversion
