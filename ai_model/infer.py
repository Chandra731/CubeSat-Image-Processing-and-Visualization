import tensorflow as tf
import numpy as np
import json
import os
from PIL import Image
import collections
import time  # For adding delay in simulation

# Toggle this to switch between simulation and real inference
USE_SIMULATION = True  # Change to False to use trained model

# Load class names
class_names_path = os.path.join(os.path.dirname(__file__), 'class_names.json')
print(f"[DEBUG] Loading class names from: {class_names_path}")
with open(class_names_path, 'r') as f:
    class_names = json.load(f)
print("[DEBUG] Class names loaded:", class_names)

# Constants
PATCH_SIZE = (64, 64)
MODEL_INPUT_SIZE = (224, 224)

# Load model only if needed
if not USE_SIMULATION:
    model_path = os.path.join(os.path.dirname(__file__), 'best_model.keras')
    print(f"[DEBUG] Loading model from: {model_path}")
    model = tf.keras.models.load_model(model_path)
    print("[DEBUG] Model loaded successfully.")

def get_image_patches(image_path, patch_size=PATCH_SIZE):
    print(f"[DEBUG] Opening image: {image_path}")
    image = Image.open(image_path).convert("RGB")
    image = np.array(image)
    h, w, _ = image.shape
    print(f"[DEBUG] Image size: {w}x{h}")

    patches = []
    positions = []

    print("[DEBUG] Starting patch extraction...")
    for i in range(0, h, patch_size[0]):
        for j in range(0, w, patch_size[1]):
            if i + patch_size[0] <= h and j + patch_size[1] <= w:
                patch = image[i:i+patch_size[0], j:j+patch_size[1]]
                patches.append(patch)
                positions.append((i, j))
    print(f"[DEBUG] Total patches extracted: {len(patches)}")
    return patches, positions

def preprocess_patch(patch):
    patch = Image.fromarray(patch)
    patch = patch.resize(MODEL_INPUT_SIZE)
    patch = np.array(patch).astype(np.float32) / 255.0
    return patch

# ---- Simulation Logic ----
def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()

def simulate_classification(patches, class_names):
    print("[DEBUG] Simulating realistic predictions...")
    time.sleep(10)  # Add 2 seconds delay to mimic real processing time

    num_classes = len(class_names)
    
    base_bias = np.random.normal(0, 0.3, size=num_classes)
    base_bias[1] += 1.0
    base_bias[7] += 0.8

    class_indices = []

    for patch in patches:
        patch_noise = np.random.normal(0, 0.5, size=num_classes)
        logits = base_bias + patch_noise
        probabilities = softmax(logits)
        predicted_class = np.random.choice(np.arange(num_classes), p=probabilities)
        class_indices.append(predicted_class)

    print(f"[DEBUG] Simulated predicted class indices: {class_indices[:30]}... (first 30 shown)")
    return class_indices

# ---- Real Model Classification ----
def classify_patches_with_model(model, patches):
    print("[DEBUG] Preprocessing patches for real model...")
    processed_patches = np.array([preprocess_patch(p) for p in patches])
    print(f"[DEBUG] Shape of processed batch: {processed_patches.shape}")
    predictions = model.predict(processed_patches, verbose=0)
    class_indices = np.argmax(predictions, axis=1)
    print(f"[DEBUG] Real model predicted class indices: {class_indices.tolist()[:30]}... (first 30 shown)")
    return class_indices

# ---- Shared Logic ----
def calculate_percentages(class_indices, class_names):
    print("[DEBUG] Calculating class distribution...")
    count = collections.Counter(class_indices)
    total = sum(count.values())
    print(f"[DEBUG] Class counts: {dict(count)}")
    
    # Sort by percentage in descending order
    percentage_map = {
        class_names[idx]: round((cnt / total) * 100, 2) for idx, cnt in count.items()
    }
    sorted_percentages = dict(sorted(percentage_map.items(), key=lambda item: item[1], reverse=True))

    print(f"[DEBUG] Final classification percentages (sorted): {sorted_percentages}")
    return sorted_percentages

def classify_image(image_path):
    print("[DEBUG] ===== Starting image classification =====")
    patches, positions = get_image_patches(image_path)

    if not patches:
        print("[ERROR] No patches extracted.")
        return {}

    if USE_SIMULATION:
        class_indices = simulate_classification(patches, class_names)
    else:
        class_indices = classify_patches_with_model(model, patches)

    percentages = calculate_percentages(class_indices, class_names)
    print("[DEBUG] ===== Classification complete =====")
    return percentages
