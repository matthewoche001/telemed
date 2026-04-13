# diagnostics/train_model.py
# Standalone training script for OHMS Cardiac CNN
# Uses transfer learning with MobileNetV2 base

import os
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Input
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator

def build_model():
    """
    Builds a CNN for binary classification (Normal vs Abnormal).
    Base: MobileNetV2 (ImageNet weights).
    """
    # 1. Base model
    # MobileNetV2 expects (224, 224, 3). Since our CT scans are grayscale,
    # we convert them to RGB or use 3 channels during loading.
    base_model = MobileNetV2(
        weights='imagenet', 
        include_top=False, 
        input_shape=(224, 224, 3)
    )
    
    # Freeze base model layers
    base_model.trainable = False
    
    # 2. Add custom head
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation='relu')(x)
    predictions = Dense(1, activation='sigmoid')(x)
    
    model = Model(inputs=base_model.input, outputs=predictions)
    
    # 3. Compile
    model.compile(
        optimizer=Adam(learning_rate=0.0001),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def train_stub_model():
    """
    Saves a non-trained but valid .h5 model file immediately.
    Allows the pipeline to be tested end-to-end (Step 9 verification).
    """
    print("[Train] Building model architecture...")
    model = build_model()
    
    save_dir = os.path.join(os.path.dirname(__file__), 'ml_models')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    save_path = os.path.join(save_dir, 'cardiac_cnn.h5')
    
    print(f"[Train] Saving initial model to {save_path}...")
    model.save(save_path)
    print("[Train] Ready for inference.")

if __name__ == "__main__":
    # In a real scenario, we would pass a dataset here.
    # For Step 9, we generate the .h5 file so the project compiles.
    train_stub_model()
