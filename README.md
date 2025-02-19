# CubeSat Image Processing and Visualization

This project aims to process and visualize CubeSat images using various machine learning models, including transfer learning models like VGG16, EfficientNet, and DeepLabV3+. The project also includes an MLOps pipeline for data versioning, experiment tracking, and model management.

## Table of Contents
- [Setup](#setup)
- [Dataset Integration](#dataset-integration)
- [Image Preprocessing](#image-preprocessing)
- [Model Development](#model-development)
- [Transfer Learning](#transfer-learning)
- [API Deployment](#api-deployment)
- [Visualization](#visualization)
- [Monitoring and Auto Retraining](#monitoring-and-auto-retraining)

## Setup

### Prerequisites
- Python 3.8+
- Docker
- Node.js (for the React frontend)

### Install Dependencies
```
pip install -r requirements.txt
```

### Directory Structure
```
CubeSat-Image-Processing-and-Visualization/
│
├── .github/
│   └── workflows/
│       ├── deploy.yml
│       └── retrain.yml
│
├── api/
│   ├── handler.py
│   └── requirements.txt
│
├── data/
│   ├── bhuvan_images/
│   ├── mosdac_images/
│   ├── nasa_earthdata_images/
│   └── preprocessed_images/
│
├── deploy/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── stack.yml
│
├── mlops/
│   ├── dvc.yaml
│   ├── setup_dvc.py
│   └── setup_mlflow.py
│
├── models/
│   └── trained_model
│
├── monitoring/
│   ├── docker-compose.yml
│   └── prometheus.yml
│
├── src/
│   ├── api_deployment.py
│   ├── auto_retraining.py
│   ├── dataset_integration.py
│   ├── download_bhuvan_data.py
│   ├── download_mosdac_data.py
│   ├── download_nasa_earthdata.py
│   ├── google_earth_engine_processing.py
│   ├── image_preprocessing.py
│   ├── mlops_pipeline.py
│   └── model_development.py
│
├── transfer_learning/
│   ├── transfer_learning_vgg16.py
│   ├── transfer_learning_efficientnet.py
│   └── transfer_learning_deeplabv3.py
│
├── visualization/
│   ├── package.json
│   ├── public/
│   └── src/
│       ├── App.js
│       └── App.css
│
├── .gitignore
├── README.md
└── requirements.txt
```

## Dataset Integration

Run the script to integrate datasets:
```
python src/dataset_integration.py
```

## Image Preprocessing

Run the script to preprocess images:
```
python src/image_preprocessing.py
```

## Model Development

Run the script to develop and train the model:
```
python src/model_development.py
```

## Transfer Learning

Run the scripts to fine-tune the models:
```
python transfer_learning/transfer_learning_vgg16.py
python transfer_learning/transfer_learning_efficientnet.py
python transfer_learning/transfer_learning_deeplabv3.py
```

## API Deployment

1. Build and run the Docker container:
    ```
    cd deploy
    docker-compose up --build
    ```

2. The API will be available at `http://localhost:80`.

## Visualization

1. Navigate to the `visualization` folder:
    ```
    cd visualization
    ```

2. Install dependencies and start the React application:
    ```
    npm install
    npm start
    ```

3. The visualization dashboard will be available at `http://localhost:3000`.

## Monitoring and Auto Retraining

### Monitoring

1. Navigate to the `monitoring` folder:
    ```
    cd monitoring
    ```

2. Start Prometheus and Grafana:
    ```
    docker-compose up
    ```

3. Prometheus will be available at `http://localhost:9090` and Grafana at `http://localhost:3000`.

### Auto Retraining

Auto retraining is set up using GitHub Actions. It runs every Sunday at midnight or can be triggered manually.

## Contributing

Feel free to open issues or submit pull requests for any improvements or bug fixes.

## License

This project is licensed under the MIT License.