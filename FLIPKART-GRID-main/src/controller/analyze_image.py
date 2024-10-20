import socketio
import jsonify
import cv2
import numpy as np
from PIL import Image
from src.scripts.identify_object import identify_object
from src.scripts.freshness_detection import predict_freshness

# from src.scripts.ocr import process_image
from src.scripts.ocr_aws import get_aws_ocr
from src.scripts.ocr_details_openai import get_product_details_from_text


def imageResults(image_array):
    # Convert the input image to a 3-channel RGB image if it's not already
    cv2.imwrite("object.jpg", image_array)
    if image_array.ndim == 2 or image_array.shape[2] == 4:  # if grayscale or RGBA
        image_array = Image.fromarray(image_array).convert("RGB")
        image_array = np.array(image_array)  # Convert back to NumPy array

    # Ensure the image is in the correct format
    if image_array.dtype != np.uint8:
        image_array = image_array.astype(np.uint8)

    # Identify the object
    predicted_class, confidence, in_list = identify_object(image_array)

    print(f"Object: {predicted_class}, Confidence: {confidence}")

    response = {}

    if in_list and confidence > 0.95:

        # Perform freshness detection
        print("Object in the list")
        (
            freshness_class,
            predicted_probability,
            adjusted_probability,
            freshness_scale,
        ) = predict_freshness(image_array)

        # if freshness_class.startswith("Fresh"):
        #     # Remove "Fresh" from the class name (e.g., FreshApple -> Apple)
        #     freshness_class = freshness_class[5:]
        # else:
        #     # Remove "Rotten" from the class name (e.g., RottenApple -> Apple)
        #     freshness_class = freshness_class[6:]

        response = {
            "name": freshness_class,
            "brand": "NA",
            "pack_size": "NA",
            "mfg_date": "NA",
            "exp_date": "NA",
            "mrp": "NA",
            "status": freshness_scale,
        }

    else:
        # Perform OCR if the object is not in the list
        print("Object not in the list")
        # ocr_text = process_image(image_array)
        ocr_text = get_aws_ocr(image_array)
        print(f"OCR Text: {ocr_text}")
        product_details = get_product_details_from_text(ocr_text)
        print(f"Product Details: {product_details}")
        response = product_details

    print("Sending response")
    print(response)
    return response
