import tensorflow as tf
import numpy as np
import os


model = tf.keras.models.Sequential([

    tf.keras.layers.Conv2D(16, (9, 9), strides=(4, 4), activation='relu', input_shape=(160, 320, 4), kernel_initializer='glorot_uniform', bias_initializer='zeros'),
    tf.keras.layers.Conv2D(32, (5, 5), strides=(2, 2), activation='relu'),
    tf.keras.layers.Conv2D(64, (5, 5), strides=(2, 2), activation='relu'),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(512, activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(1)
])



opt = tf.keras.optimizers.Adam(lr=0.00001)

model.compile(loss = 'mean_squared_error',
              optimizer = opt
              )

WEIGHTS = os.path.join(os.path.dirname(__file__), 'savedWeights/weights.json')
model.load_weights(WEIGHTS)

def process_image(camera_image):
    numpy_image = np.asarray(camera_image)
    normalized_image = (numpy_image / 255.0) - 0.5
    processed_image = np.expand_dims(normalized_image, axis=0)
    return processed_image

def predict_model(camera_image):
    processed_image = process_image(camera_image)
    steer = model.predict(processed_image)
    steering_angle = float(steer[0][0])
    print ('Predicted Steering angle: ',steering_angle)
    return steering_angle