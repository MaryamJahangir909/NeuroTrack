import tensorflow as tf
import numpy as np
from PIL import Image
import sys

# Load the trained model
print("🧠 Loading trained model...")
model = tf.keras.models.load_model('trained_model/neurotrack_model.h5')

# Class names (MUST match training order)
CLASS_NAMES = ['glioma', 'meningioma', 'notumor', 'pituitary']

def predict_image(image_path):
    # Load and resize image
    img = Image.open(image_path).convert('RGB')
    img = img.resize((224, 224))
    
    # Convert to array and normalize
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    # Predict
    prediction = model.predict(img_array, verbose=0)
    
    # Get results
    predicted_class_index = np.argmax(prediction[0])
    confidence = prediction[0][predicted_class_index] * 100
    predicted_class_name = CLASS_NAMES[predicted_class_index]
    
    return predicted_class_name, confidence, prediction[0]

if __name__ == "__main__":
    # Use an image from the Testing set
    # Change this path to test different images
    test_image = "dataset/Testing/notumor/Te-no_100.jpg"
    
    print(f"\n📸 Analyzing: {test_image}")
    print("-" * 40)
    
    name, conf, probs = predict_image(test_image)
    
    print(f"✅ PREDICTION: {name.upper()}")
    print(f"📊 CONFIDENCE: {conf:.2f}%")
    print("-" * 40)
    print("Detailed Probabilities:")
    for i, class_name in enumerate(CLASS_NAMES):
        print(f"  {class_name:12} : {probs[i]*100:.2f}%")