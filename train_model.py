import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers, models
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
import os

# Paths
DATASET_PATH = 'dataset'
MODEL_SAVE_PATH = 'trained_model/neurotrack_model.h5'
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 10

print("🧠 NeuroTrack - Starting Model Training...")
print("=" * 50)

# Data preparation
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=15,
    width_shift_range=0.1,
    height_shift_range=0.1,
    horizontal_flip=True,
    validation_split=0.2
)

test_datagen = ImageDataGenerator(rescale=1./255)

print("📂 Loading Training Data...")
train_generator = train_datagen.flow_from_directory(
    os.path.join(DATASET_PATH, 'Training'),
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training'
)

print("📂 Loading Validation Data...")
val_generator = train_datagen.flow_from_directory(
    os.path.join(DATASET_PATH, 'Training'),
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation'
)

print(f"✅ Classes found: {train_generator.class_indices}")
print(f"✅ Training images: {train_generator.samples}")
print(f"✅ Validation images: {val_generator.samples}")

# Build model using MobileNetV2
print("\n🔧 Building CNN Model...")

base_model = MobileNetV2(
    weights='imagenet',
    include_top=False,
    input_shape=(224, 224, 3)
)
base_model.trainable = False

model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.3),
    layers.Dense(4, activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print("✅ Model built successfully!")
model.summary()

# Callbacks
callbacks = [
    ModelCheckpoint(
        MODEL_SAVE_PATH,
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    ),
    EarlyStopping(
        monitor='val_accuracy',
        patience=3,
        verbose=1
    )
]

# Train
print("\n🚀 Training Started...")
history = model.fit(
    train_generator,
    epochs=EPOCHS,
    validation_data=val_generator,
    callbacks=callbacks,
    verbose=1
)

print("\n✅ Training Complete!")
print(f"✅ Model saved to: {MODEL_SAVE_PATH}")