# CubeSat Onboard AI Image Classification and 3D Visualization

## Project Title and Summary

CubeSat Onboard AI Image Classification and 3D Visualization is a full-stack platform designed for Earth observation using CubeSats. It features onboard AI image classification and interactive 3D visualization of satellite orbits and data.

---

## High-Level Architecture

The system is composed of four main components:

- **Frontend:** Web application built with Flask, CesiumJS, Bootstrap, and Chart.js for 3D visualization, image capture, classification, and user management.

- **Backend:** Flask REST API server managing CubeSat data, user authentication, image uploads, classification integration, and history management, backed by SQLite.

- **AI Model:** EfficientNet-B0 based TensorFlow/Keras model trained on EuroSAT dataset for satellite image classification, with simulation mode for inference.

- **Data:** Satellite TLE data, uploaded images, and classification results stored in the database and filesystem.

---

## Technology Stack

- Python 3.x, Flask, SQLAlchemy, TensorFlow/Keras
- JavaScript, CesiumJS, Leaflet, Chart.js, Bootstrap 5
- SQLite database
- Google Earth Engine integration
- RESTful API design

---

## Folder Structure

- `/frontend` - Frontend web app with templates, static assets, and client-side JavaScript.
- `/backend` - Backend API server with routes, models, database, and utilities.
- `/ai_model` - AI model code for image classification.

---

## Setup Instructions

1. **Backend Setup:**

   - Navigate to `/backend`.
   - Install dependencies: `pip install -r requirements.txt`.
   - Configure environment variables if needed (e.g., `DATABASE_URL`, email credentials).
   - Run the backend server: `python app.py`.

2. **AI Model Setup:**

   - Navigate to `/ai_model`.
   - Install TensorFlow and dependencies.
   - Use `infer.py` for image classification.
   - Training is done externally (e.g., Google Colab). See `Model-Building.ipynb` for training pipeline.

3. **Frontend Setup:**

   - Navigate to `/frontend`.
   - Install dependencies if any.
   - Run the frontend server: `python app.py`.
   - Access via browser at `http://127.0.0.1:5000`.

---

## How the Components Interact

- Frontend communicates with Backend API for data, authentication, image upload, and classification.
- Backend integrates AI Model for image classification via API endpoint.
- Backend fetches and updates satellite TLE data for visualization.
- Frontend visualizes satellite orbits and data using CesiumJS and charts.

---

## Features List

- Real-time 3D visualization of CubeSat orbits and positions.
- Satellite image capture and AI-based classification.
- User authentication and session management.
- Image and classification history with filtering and management.
- Automated TLE data updates.
- Responsive and interactive UI.

---

## Future Roadmap

- Enhance AI model training and deployment.
- Add more datasets and classification categories.
- Improve UI/UX and mobile responsiveness.
- Implement advanced satellite analytics and alerts.
- Integrate with additional satellite data sources.
