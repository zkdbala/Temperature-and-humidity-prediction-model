import tensorflow as tf
import numpy as np


def normalize_data(data):

    # Convert input data to numpy array
    data = np.array(data)

    # Calculate mean and standard deviation of input data
    data_mean = np.mean(data)
    data_std = np.std(data)

    # Normalize input data using z-score formula
    normalized_data = (data - data_mean) / data_std

    return normalized_data


def unnormalize_data(normalized_data, original_data):

    # Convert input data to numpy arrays
    normalized_data = np.array(normalized_data)
    original_data = np.array(original_data)

    # Calculate mean and standard deviation of original data
    original_mean = np.mean(original_data)
    original_std = np.std(original_data)

    # Unnormalize input data using z-score formula
    unnormalized_data = (normalized_data * original_std) + original_mean

    return unnormalized_data


# load saved model
model = tf.keras.models.load_model("saved_model")


def predict(data):
    data = tf.convert_to_tensor(data)
    ans = model.predict(data)
    return ans


def prediction(original_data, n):
    normalized_data = normalize_data(original_data)
    normalized_output = predict(normalized_data)
    unnormalized_output = unnormalize_data(normalized_output, original_data)
    ans = [unnormalized_output[0].tolist()]

    for _ in range(n-1):
        temp = original_data[0][1:]
        temp.append(unnormalized_output[0])
        original_data = [temp]
        normalized_data = normalize_data(original_data)
        normalized_output = predict(normalized_data)
        unnormalized_output = unnormalize_data(
            normalized_output, original_data)
        ans.append(unnormalized_output[0].tolist())

    return ans
