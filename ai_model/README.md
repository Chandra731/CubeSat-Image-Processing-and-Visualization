# AI Model - CubeSat Visualization Platform

This directory contains the AI model code for satellite image classification used in the CubeSat Visualization Platform.

---

## Overview

The AI model performs image classification on satellite imagery patches to identify land cover or other relevant classes. It supports both real model inference and a simulation mode for testing.

---

## Features

- Patch-based image classification using TensorFlow Keras.
- Simulation mode to generate realistic classification results without a trained model.
- Model training notebook included for building and training the model.
- Class names stored in a JSON file for easy modification.
- Integration with backend API for classification requests.

---

## Files

- `infer.py`  
  - Loads class names and a trained model.
  - Extracts patches from input images.
  - Performs classification using the model or simulation.
  - Returns classification percentages.

- `train.py`  
  - Placeholder script for model training (currently prints a message).
  - Intended for use in external environments like Google Colab.

- `Model-Building.ipynb`
  - Jupyter notebook containing the full model training pipeline.

- `preprocess.py`  
  - contains image preprocessing utilities.

- `class_names.json`  
  - JSON file listing class names used for classification.

- `api.py`  
  - provides API interface for model serving.

---

## Usage

- To classify an image, call `classify_image(image_path)` in `infer.py`.
- Set `USE_SIMULATION` flag in `infer.py` to toggle between simulation and real model inference.
- Training can be done using the included Jupyter notebook `Model-Building.ipynb`.

---

## Notes

- The model expects image patches of size 64x64 resized to 224x224 for input.
- Simulation mode adds realistic random predictions with delay for testing.
- Backend API `/classify_image` endpoint integrates this inference functionality.
