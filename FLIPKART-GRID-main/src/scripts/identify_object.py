import tensorflow as tf
import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image

# Step 2: Load Models
fine_tuned_model = load_model("src/models/identification_mobilenet_finetuned.keras")
base_model = load_model("src/models/identification_mobilenet_v2.keras")

# Define the classes for your fine-tuned model
fine_tuned_classes = {
    "Apple": 0,
    "Carrot": 1,
    "FMCG": 2,
    "Grape": 3,
    "Guava": 4,
    "Ladyfinger": 5,
    "Mango": 6,
    "Potato": 7,
    "Tomato": 8,
}

# Define the classes you want the integrated model to detect
integrated_classes = [
    "Apple",
    "Banana",
    "Grape",
    "Guava",
    "Mango",
    "Orange",
    "Pomegranate",
    "Strawberry",
    "Bell Pepper",
    "Carrot",
    "Cucumber",
    "Ladyfinger",
    "Potato",
    "Tomato",
]


# Step 3: Preprocessing function for MobileNet
def preprocess_image(image_array):
    img = Image.fromarray(image_array)
    img = img.resize((224, 224))
    img_array = np.array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = tf.keras.applications.mobilenet.preprocess_input(img_array)
    return img_array


# Step 4: Prediction function
def predict_image_class(image_array, weight_factor=1.2):
    """
    Predict the class of an image using the fine-tuned and base models.

    Args:
        image_array (np.array): Input image as a NumPy array.
        weight_factor (float): Factor to weight the base model's confidence.

    Returns:
        str, float, bool: The predicted class, the associated confidence, and whether it is in the list.
    """
    # Preprocess the image
    img_array = preprocess_image(image_array)

    # Get predictions from fine-tuned model
    fine_tuned_preds = fine_tuned_model.predict(img_array)
    fine_tuned_class_idx = np.argmax(fine_tuned_preds)
    fine_tuned_confidence = np.max(fine_tuned_preds)

    # Map index to class name for fine-tuned model
    fine_tuned_class = list(fine_tuned_classes.keys())[fine_tuned_class_idx]

    print(
        f"Fine-tuned model prediction: {fine_tuned_class} with confidence: {fine_tuned_confidence:.2f}"
    )

    # Store fine-tuned result in the ans variable
    ans = {
        "class": fine_tuned_class,
        "confidence": fine_tuned_confidence,
        "in_list": fine_tuned_class in integrated_classes,
    }

    # Get predictions from base MobileNetV2 model
    base_preds = base_model.predict(img_array)
    decoded_preds = tf.keras.applications.mobilenet_v2.decode_predictions(
        base_preds, top=1
    )[0][0]
    base_class = decoded_preds[1]
    base_confidence = decoded_preds[2]

    # Adjust 'bell pepper' class name to 'Capsicum'
    if base_class.lower() == "bell pepper":
        base_class = "Capsicum"

    print(f"Base model prediction: {base_class} with confidence: {base_confidence:.2f}")

    # Apply weight factor to the base model confidence for comparison
    weighted_base_confidence = base_confidence * weight_factor

    # Compare the weighted confidence with the fine-tuned model's confidence
    if weighted_base_confidence > ans["confidence"]:
        ans = {
            "class": base_class,
            "confidence": base_confidence,
            "in_list": base_class in integrated_classes,
        }

    # Return the class with the higher (weighted) confidence
    return ans["class"], ans["confidence"], ans["in_list"]


def identify_object(image_array):
    predicted_class, confidence, in_list = predict_image_class(image_array)
    return predicted_class, confidence, in_list


if __name__ == "__main__":
    image_array = np.array(
        Image.open("src/scripts/image.png")
    )  # Replace this line with your NumPy array image input
    predicted_class, confidence, in_list = predict_image_class(image_array)
    print(f"Predicted class: {predicted_class} with confidence: {confidence:.2f}")
    print(f"Is the predicted class in the list? {in_list}")

# # Example Usage:
# image_array = np.array(
#     Image.open("src/scripts/compressed_8.jpg")
# )  # Replace this line with your NumPy array image input
# predicted_class, confidence = predict_image_class(image_array)
# print(f"Predicted class: {predicted_class} with confidence: {confidence:.2f}")
