import keras
import tensorflow as tf
import numpy as np
from sklearn.model_selection import train_test_split
import keras.backend as K
from keras.layers import (
    Input,
    Conv2D,
    MaxPooling2D,
    UpSampling2D,
    Flatten,
    Dense,
    Reshape,
    ZeroPadding2D,
)
from keras.models import Model
from keras.optimizers import RMSprop
from tensorflow.keras.datasets import mnist

(x_train, _), (x_test, _) = mnist.load_data()
x_train = x_train[:5000]
x_test = x_test[:5000]

x_train = x_train.astype("float32") / 255.0
x_test = x_test.astype("float32") / 255.0

x_train = np.expand_dims(x_train, axis=-1)
x_test = np.expand_dims(x_test, axis=-1)

train_X, test_data = train_test_split(x_train, test_size=0.2, random_state=13)

epochs = 10
batch_size = 64
latent_dimension = 10
layers = 3
filters_per_layer = 32
filter_size = 3

# Seed definition
np.random.seed(42)
tf.random.set_seed(42)

input_img = Input(shape=(28, 28, 1))


def autoencoder(image, filters_per_layer, layers, filter_size, latent_dimension):
    conv = []
    pool = []
    conv.append(
        Conv2D(
            filters_per_layer,
            (filter_size, filter_size),
            activation="relu",
            padding="same",
        )(image)
    )
    pool.append(MaxPooling2D(pool_size=(2, 2))(conv[0]))

    for i in range(1, layers - 1):
        conv.append(
            Conv2D(
                2**i * filters_per_layer,
                (filter_size, filter_size),
                activation="relu",
                padding="same",
            )(pool[i - 1])
        )
        pool.append(MaxPooling2D(pool_size=(2, 2))(conv[i]))

    conv.append(
        Conv2D(
            2 ** (layers - 1) * filters_per_layer,
            (filter_size, filter_size),
            activation="relu",
            padding="same",
        )(pool[-1])
    )

    flat = Flatten()(conv[-1])
    dense = Dense(latent_dimension, activation="relu")(flat)

    return (dense, conv[-1].shape[1:], image.shape[1])


def decoder(encoder_res, filters_per_layer, layers, filter_size):
    encoded = encoder_res[0]
    target_shape = encoder_res[1]
    image_dimension = encoder_res[2]

    dense_units = target_shape[0] * target_shape[1] * target_shape[2]
    dense = Dense(dense_units, activation="relu")(encoded)
    reshaped = Reshape((target_shape[0], target_shape[1], target_shape[2]))(dense)

    conv = []
    up = []
    conv.append(
        Conv2D(
            filters_per_layer,
            (filter_size, filter_size),
            activation="relu",
            padding="same",
        )(reshaped)
    )
    up.append(UpSampling2D((2, 2))(conv[0]))

    for i in range(1, layers - 1):
        conv.append(
            Conv2D(
                (2 ** (layers - i - 1)) * filters_per_layer,
                (filter_size, filter_size),
                activation="relu",
                padding="same",
            )(up[i - 1])
        )
        up.append(UpSampling2D((2, 2))(conv[i]))

    decoded = Conv2D(
        1, (filter_size, filter_size), activation="sigmoid", padding="same"
    )(up[-1])
    padding_size = int((image_dimension - decoded.shape[1]) / 2)
    padded_decoded = ZeroPadding2D(
        padding=((padding_size, padding_size), (padding_size, padding_size))
    )(decoded)

    return padded_decoded


autoencoder_model = Model(
    input_img,
    decoder(
        autoencoder(
            input_img, filters_per_layer, layers, filter_size, latent_dimension
        ),
        filters_per_layer,
        layers,
        filter_size,
    ),
)
autoencoder_model.compile(loss="mean_squared_error", optimizer=RMSprop())

autoencoder_train = autoencoder_model.fit(
    train_X,
    train_X,
    batch_size=batch_size,
    epochs=epochs,
    verbose=1,
    validation_data=(test_data, test_data),
)

autoencoder_model.save_weights("autoencoder.weights.h5")

score = autoencoder_model.evaluate(test_data, test_data, verbose=1)
print("Score:", score)

encoder_model = autoencoder_model
encoder_model.load_weights("autoencoder.weights.h5")

encoded_train_images = encoder_model.predict(x_train)
encoded_test_images = encoder_model.predict(x_test)

encoded_train_images = (encoded_train_images * 255).astype(np.uint8).flatten()
