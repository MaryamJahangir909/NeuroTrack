import tensorflow as tf
import numpy as np
import cv2
import os
import base64
from PIL import Image


class GradCAM:
    def __init__(self, model):
        self.model = model
        self.grad_model = None
        self.last_conv_layer = None
        self._setup()

    def _setup(self):
        try:
            print("Setting up Grad-CAM...")

            # Warm up with dummy input
            dummy = tf.zeros((1, 224, 224, 3))
            _ = self.model(dummy)
            print("Model warmed up")

            # Get MobileNetV2 (first layer of our sequential model)
            mobilenet = self.model.layers[0]

            # Warm up mobilenet too
            _ = mobilenet(dummy)
            print("MobileNet warmed up")

            # Find last conv layer in MobileNet
            for layer in reversed(mobilenet.layers):
                if isinstance(layer, tf.keras.layers.Conv2D):
                    self.last_conv_layer = layer.name
                    break

            if self.last_conv_layer is None:
                self.last_conv_layer = 'Conv_1'

            print(f"Last conv layer: {self.last_conv_layer}")

            # Build grad model using functional API
            input_layer = tf.keras.Input(shape=(224, 224, 3))

            # Pass through mobilenet to get conv output
            conv_layer = mobilenet.get_layer(self.last_conv_layer)

            # Create a model that outputs both conv features and final predictions
            mobilenet_out = mobilenet(input_layer)

            # Pass through rest of the layers (after MobileNetV2)
            x = mobilenet_out
            for layer in self.model.layers[1:]:
                x = layer(x)

            # Now create a model with both outputs
            conv_output = conv_layer.output

            # Alternative: Use intermediate model approach
            intermediate_model = tf.keras.Model(
                inputs=mobilenet.input,
                outputs=conv_layer.output
            )

            self.intermediate_model = intermediate_model
            print("Grad-CAM setup complete!")

        except Exception as e:
            print(f"Grad-CAM setup error: {e}")
            self.intermediate_model = None

    def generate_heatmap(self, image_path, class_index):
        try:
            # Load original
            original_img = cv2.imread(image_path)
            if original_img is None:
                return None
            original_img = cv2.resize(original_img, (224, 224))

            # Preprocess
            img = Image.open(image_path).convert('RGB')
            img = img.resize((224, 224))
            img_array = np.array(img, dtype=np.float32) / 255.0
            img_batch = np.expand_dims(img_array, axis=0)

            # Try real Grad-CAM
            heatmap = self._gradcam_v2(img_batch, class_index)

            # If failed, use occlusion fallback
            if heatmap is None:
                print("Using occlusion fallback")
                heatmap = self._occlusion_heatmap(img_batch, class_index)

            if heatmap is None:
                return None

            # Resize and process
            heatmap = cv2.resize(heatmap, (224, 224))
            heatmap = cv2.GaussianBlur(heatmap, (11, 11), 0)
            heatmap_uint8 = np.uint8(255 * heatmap)
            heatmap_colored = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)

            superimposed = cv2.addWeighted(
                original_img, 0.55,
                heatmap_colored, 0.45,
                0
            )

            return superimposed, heatmap

        except Exception as e:
            print(f"Heatmap error: {e}")
            return None

    def _gradcam_v2(self, img_batch, class_index):
        """Real Grad-CAM using gradient computation"""
        try:
            if self.intermediate_model is None:
                return None

            img_tensor = tf.convert_to_tensor(img_batch)
            mobilenet = self.model.layers[0]

            with tf.GradientTape() as tape:
                tape.watch(img_tensor)
                # Get conv features
                conv_output = self.intermediate_model(img_tensor)
                # Get full prediction
                predictions = self.model(img_tensor)
                # Score for target class
                class_score = predictions[:, class_index]

            # Compute gradients
            grads = tape.gradient(class_score, conv_output)

            if grads is None:
                print("Gradients are None")
                return None

            # Pool gradients globally
            pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

            # Weight conv outputs by pooled gradients
            conv_output = conv_output[0]
            heatmap = tf.reduce_sum(
                tf.multiply(pooled_grads, conv_output),
                axis=-1
            )

            # Apply ReLU
            heatmap = tf.nn.relu(heatmap)

            # Normalize
            heatmap = heatmap.numpy()
            if heatmap.max() > 0:
                heatmap = heatmap / heatmap.max()

            print("Real Grad-CAM generated!")
            return heatmap

        except Exception as e:
            print(f"Grad-CAM v2 failed: {e}")
            return None

    def _occlusion_heatmap(self, img_batch, class_index):
        """Occlusion-based heatmap (fallback)"""
        try:
            img = img_batch[0]
            h, w = 224, 224
            patch_size = 28
            stride = 14
            heatmap = np.zeros((h, w), dtype=np.float32)
            count_map = np.zeros((h, w), dtype=np.float32)

            original_pred = self.model.predict(img_batch, verbose=0)
            original_score = float(original_pred[0][class_index])

            for y in range(0, h - patch_size + 1, stride):
                for x in range(0, w - patch_size + 1, stride):
                    occluded = img.copy()
                    occluded[y:y + patch_size, x:x + patch_size, :] = 0.5
                    occluded_batch = np.expand_dims(occluded, axis=0)
                    occluded_pred = self.model.predict(occluded_batch, verbose=0)
                    occluded_score = float(occluded_pred[0][class_index])
                    importance = max(0, original_score - occluded_score)
                    heatmap[y:y + patch_size, x:x + patch_size] += importance
                    count_map[y:y + patch_size, x:x + patch_size] += 1

            count_map[count_map == 0] = 1
            heatmap = heatmap / count_map

            if heatmap.max() > 0:
                heatmap = heatmap / heatmap.max()

            return heatmap

        except Exception as e:
            print(f"Occlusion error: {e}")
            return None

    def save_heatmap(self, image_path, class_index, scan_id):
        try:
            result = self.generate_heatmap(image_path, class_index)
            if result is None:
                return None

            superimposed, heatmap = result

            heatmap_folder = 'uploads/heatmaps'
            os.makedirs(heatmap_folder, exist_ok=True)

            heatmap_filename = f'heatmap_{scan_id}.jpg'
            heatmap_path = os.path.join(heatmap_folder, heatmap_filename)

            cv2.imwrite(heatmap_path, superimposed)
            print(f"Heatmap saved: {heatmap_path}")

            with open(heatmap_path, 'rb') as f:
                image_data = f.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')

            return {
                'heatmap_path': heatmap_path,
                'heatmap_filename': heatmap_filename,
                'base64': f'data:image/jpeg;base64,{base64_image}'
            }

        except Exception as e:
            print(f"Save heatmap error: {e}")
            return None