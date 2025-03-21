import tensorflow as tf
from preprocess import preprocess_image

# Placeholder model loading
# Replace with actual model path after training in Google Colab
model = tf.keras.models.load_model('model_placeholder.h5')

def classify_image(image_path):
    image = preprocess_image(image_path)
    prediction = model.predict(image)
    class_names = ['Urban', 'Water bodies', 'Forest', 'Agricultural land', 'Barren land', 'Cloud cover']
    predicted_class = class_names[np.argmax(prediction)]
    confidence = np.max(prediction) * 100
    return predicted_class, confidence