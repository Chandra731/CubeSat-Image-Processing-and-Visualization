# 🌍 CubeSat Visualization Backend 🚀

## 📌 Overview
This is the backend for the CubeSat Visualization project. It:
- Fetches **CubeSat orbital data** from Celestrak.
- Stores data in a **database** for easy retrieval.
- Captures **satellite images** using Google Earth Engine.
- Provides an **image history** feature.
- Sends images for **classification** (AI-based in the future).

---

## ⚙️ Tech Stack
- **Python** (Flask)
- **SQLAlchemy** (Database ORM)
- **Google Earth Engine** (Image Capture)
- **Celery + Redis** (Background Tasks)

---

## 🚀 Installation

### 1️⃣ Clone the Repository
```sh
git clone https://github.com/your-username/cubesat-visualization.git
cd cubesat-visualization/backend
```

### 2️⃣ Set Up Virtual Environment
```sh
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows
```

### 3️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

### 4️⃣ Set Up Environment Variables
Create a `.env` file and add:
```ini
DATABASE_URL=sqlite:///database.db
EARTH_ENGINE_PROJECT=your-google-earth-engine-project
```

### 5️⃣ Initialize Database
```sh
python -c "from database import init_db; init_db()"
```

### 6️⃣ Fetch CubeSat Data
```sh
python fetch_tle.py
```

### 7️⃣ Run Flask App
```sh
flask run
```
App runs on [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

---

## 📡 API Endpoints

### 🚀 CubeSat Data
| Method | Endpoint             | Description          |
|--------|----------------------|----------------------|
| GET    | /cubesat_positions   | Fetch CubeSat data   |

### 🌍 Image Handling
| Method | Endpoint             | Description                      |
|--------|----------------------|----------------------------------|
| POST   | /capture_image       | Capture an image using Google Earth Engine |
| GET    | /image_history       | View captured image history      |

### 🔍 Classification
| Method | Endpoint             | Description                      |
|--------|----------------------|----------------------------------|
| POST   | /classify_image      | Classify an image using AI       |

---

## 📜 License
MIT License.

---

## 🤝 Contribution Guidelines
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a Pull Request.

---

## 📝 Additional Notes
- Ensure you have the necessary permissions and access to Google Earth Engine.
- Consider setting up a virtual environment to manage dependencies.
- Regularly update the `requirements.txt` file with any new dependencies.

### Common Commands
- To activate the virtual environment:
  ```sh
  source venv/bin/activate  # macOS/Linux
  venv\Scripts\activate  # Windows
  ```
- To deactivate the virtual environment:
  ```sh
  deactivate
  ```

---

## 📞 Support
For any questions or support, please open an issue on the repository or contact the maintainer.
