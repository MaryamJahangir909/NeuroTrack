import tensorflow as tf
import numpy as np
from PIL import Image
import os

CLASS_NAMES = ['glioma', 'meningioma', 'notumor', 'pituitary']


class TumorPredictor:
    def __init__(self):
        self.model = None
        self.model_path = 'trained_model/neurotrack_model.h5'
        self.gradcam = None
        self.load_model()

    def load_model(self):
        try:
            if os.path.exists(self.model_path):
                self.model = tf.keras.models.load_model(self.model_path)
                print("Model loaded successfully")
                from gradcam import GradCAM
                self.gradcam = GradCAM(self.model)
            else:
                print("Model not found. Train the model first.")
        except Exception as e:
            print(f"Error loading model: {e}")

    def is_valid_mri(self, image_path):
        try:
            img = Image.open(image_path).convert('RGB')
            img_small = img.resize((224, 224))
            img_array = np.array(img_small)

            r = img_array[:, :, 0].astype(float)
            g = img_array[:, :, 1].astype(float)
            b = img_array[:, :, 2].astype(float)

            avg_color_diff = (
                np.mean(np.abs(r - g)) +
                np.mean(np.abs(r - b)) +
                np.mean(np.abs(g - b))
            ) / 3

            if avg_color_diff > 30:
                return False, "This does not appear to be a medical scan."

            h, w = img_array.shape[:2]
            center = img_array[h//4:3*h//4, w//4:3*w//4]
            edges = np.concatenate([
                img_array[:h//4, :].flatten(),
                img_array[3*h//4:, :].flatten(),
                img_array[:, :w//4].flatten(),
                img_array[:, 3*w//4:].flatten()
            ])

            center_brightness = np.mean(center)
            edge_brightness = np.mean(edges)
            brightness_ratio = center_brightness / (edge_brightness + 1)

            if brightness_ratio < 0.8:
                return False, "Image pattern does not match brain MRI."

            return True, "Valid"

        except Exception as e:
            return False, f"Error: {str(e)}"

    def predict(self, image_path):
        if self.model is None:
            raise RuntimeError("Model not loaded")

        is_valid, message = self.is_valid_mri(image_path)
        if not is_valid:
            return {
                'error': True,
                'message': message
            }

        img = Image.open(image_path).convert('RGB')
        img = img.resize((224, 224))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        prediction = self.model.predict(img_array, verbose=0)

        predicted_index = np.argmax(prediction[0])
        predicted_class = CLASS_NAMES[predicted_index]
        confidence = float(prediction[0][predicted_index])

        if confidence < 0.85:
            return {
                'error': True,
                'message': 'Low confidence. Please upload a clear brain MRI scan.'
            }

        sorted_probs = sorted(prediction[0], reverse=True)
        top_two_diff = sorted_probs[0] - sorted_probs[1]

        if top_two_diff < 0.3:
            return {
                'error': True,
                'message': 'Unable to classify confidently.'
            }

        return {
            'error': False,
            'predicted_class': predicted_class,
            'confidence': confidence,
            'is_tumor': predicted_class != 'notumor',
            'probabilities': {
                'glioma': float(prediction[0][0]),
                'meningioma': float(prediction[0][1]),
                'notumor': float(prediction[0][2]),
                'pituitary': float(prediction[0][3])
            }
        }


predictor = TumorPredictor()