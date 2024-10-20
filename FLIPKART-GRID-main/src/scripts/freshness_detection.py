import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.mobilenet import preprocess_input
from tensorflow.keras.preprocessing import image
from PIL import Image

# Load the model
model_path = "src/models/freshness_detection_model.keras"  # Update path as needed
model = load_model(model_path)

# Define class indices
class_indices = {
    "FreshApple": 0,
    "FreshBanana": 1,
    "FreshCapsicum": 2,
    "FreshCarrot": 3,
    "FreshCucumber": 4,
    "FreshGrape": 5,
    "FreshGuava": 6,
    "FreshLadyfinger": 7,
    "FreshMango": 8,
    "FreshOrange": 9,
    "FreshPomegranate": 10,
    "FreshPotato": 11,
    "FreshStrawberry": 12,
    "FreshTomato": 13,
    "RottenApple": 14,
    "RottenBanana": 15,
    "RottenCapsicum": 16,
    "RottenCarrot": 17,
    "RottenCucumber": 18,
    "RottenGrape": 19,
    "RottenGuava": 20,
    "RottenLadyfinger": 21,
    "RottenMango": 22,
    "RottenOrange": 23,
    "RottenPomegranate": 24,
    "RottenPotato": 25,
    "RottenStrawberry": 26,
    "RottenTomato": 27,
}

# Reverse the class_indices for easy lookup
index_to_class = {v: k for k, v in class_indices.items()}


def preprocess_image(image_array):
    """Preprocess the image NumPy array for the MobileNet model."""
    img = Image.fromarray(image_array)
    img = img.resize((224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    return preprocess_input(img_array)


def get_freshness_scale(adjusted_probability):
    """Return the freshness scale based on the adjusted probability score."""
    if 90 <= adjusted_probability <= 100:
        return "A+ (Super Fresh)"
    elif 80 <= adjusted_probability < 90:
        return "A (Fresh)"
    elif 60 <= adjusted_probability < 80:
        return "B (Medium Fresh)"
    elif 40 <= adjusted_probability < 60:
        return "C (Stale)"
    else:
        return "D (Rotten)"


def predict_freshness(image_array):
    """Predict the freshness of the uploaded image (NumPy array) and give the most suitable class and freshness scale."""
    # Preprocess the image
    preprocessed_image = preprocess_image(image_array)

    # Get predictions
    predictions = model.predict(preprocessed_image)[0]

    # Get the predicted class and its probability
    predicted_index = np.argmax(predictions)
    predicted_class = index_to_class[predicted_index]
    predicted_probability = predictions[predicted_index] * 100

    # Separate probabilities of fresh and rotten classes
    fresh_indices = [i for i, label in index_to_class.items() if "Fresh" in label]
    rotten_indices = [i for i, label in index_to_class.items() if "Rotten" in label]

    # Calculate the sum of probabilities for fresh and rotten classes
    fresh_sum = np.sum([predictions[i] for i in fresh_indices]) * 100
    rotten_sum = np.sum([predictions[i] for i in rotten_indices]) * 100

    # Adjusted probability calculation
    if "Fresh" in predicted_class:
        # Highest fresh probability minus total rotten probabilities
        highest_fresh_probability = (
            np.max([predictions[i] for i in fresh_indices]) * 100
        )
        adjusted_probability = highest_fresh_probability - rotten_sum
    else:  # Predicted class is "Rotten"
        # Highest rotten probability minus total fresh probabilities
        highest_rotten_probability = (
            np.max([predictions[i] for i in rotten_indices]) * 100
        )
        adjusted_probability = 100 - highest_rotten_probability - fresh_sum

    # Clip the adjusted probability between 0 and 100 to avoid negative scores
    adjusted_probability = np.clip(adjusted_probability, 0, 100)

    # Get the freshness scale based on the adjusted probability
    freshness_scale = get_freshness_scale(adjusted_probability)

    return predicted_class, predicted_probability, adjusted_probability, freshness_scale


if __name__ == "__main__":
    # Example Usage:
    image_array = np.array(
        Image.open("src/scripts/img.jpeg")
    )  # Replace this with your NumPy array input
    predicted_class, predicted_probability, adjusted_probability, freshness_scale = (
        predict_freshness(image_array)
    )
    print(f"Predicted Class: {predicted_class}")
    print(f"Probability Score: {predicted_probability:.2f}%")
    print(f"Freshness Percentage: {adjusted_probability:.2f}%")
    print(f"Freshness Scale: {freshness_scale}")
