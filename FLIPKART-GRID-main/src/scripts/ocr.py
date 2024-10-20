import cv2
import torch
import torchvision.transforms as T
import numpy as np
from easyocr import Reader
import os


# 1. U-Net model definition
class UNetEnhancer(torch.nn.Module):
    def __init__(self):
        super(UNetEnhancer, self).__init__()
        # Define the U-Net architecture here
        # For simplicity, using a dummy layer; replace with actual architecture.
        self.layer = torch.nn.Conv2d(3, 3, 3, padding=1)

    def forward(self, x):
        return self.layer(x)


# 2. Load U-Net model (locally if exists, or train/download and save it locally)
MODEL_PATH = "src/models/ocr_unet.pth"


def load_unet_model():
    model = UNetEnhancer()
    if os.path.exists(MODEL_PATH):
        model.load_state_dict(torch.load(MODEL_PATH, weights_only=True))
        print("U-Net model loaded from local storage.")
    else:
        # Assume you've trained/downloaded U-Net; for now, it's randomly initialized.
        print("Saving randomly initialized U-Net model.")
        torch.save(model.state_dict(), MODEL_PATH)
    return model


# Preprocessing function with OpenCV
def preprocess_image(image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced_img = clahe.apply(gray)

    # Denoise image
    denoised = cv2.GaussianBlur(enhanced_img, (5, 5), 0)

    # Binarization
    _, binary_img = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Convert back to 3-channel image
    final_img = cv2.cvtColor(binary_img, cv2.COLOR_GRAY2BGR)

    return final_img


# U-Net enhancement
def enhance_image_with_unet(image, model):
    # Convert image to tensor and normalize
    transform = T.ToTensor()
    image_tensor = transform(image).unsqueeze(0)  # Add batch dimension
    enhanced_tensor = model(image_tensor)

    # Convert back to numpy
    enhanced_img = enhanced_tensor.squeeze(0).permute(1, 2, 0).detach().numpy()
    enhanced_img = (enhanced_img * 255).astype(np.uint8)  # Scale back to [0, 255]
    return enhanced_img


# OCR with EasyOCR
def perform_ocr(image):
    reader = Reader(["en"])  # Initialize EasyOCR with English
    results = reader.readtext(image)

    # Extract only the detected text from the results
    detected_text = [text for (_, text, _) in results]
    return detected_text


# Full processing pipeline
def process_image(image_array):
    # Step 1: Preprocess with OpenCV
    preprocessed_image = preprocess_image(image_array)

    # Step 2: Enhance with U-Net
    unet_model = load_unet_model()
    enhanced_image = enhance_image_with_unet(preprocessed_image, unet_model)

    # Step 3: Perform OCR
    ocr_results = perform_ocr(enhanced_image)

    # convert list to string
    ocr_results = " ".join(ocr_results)

    # Return OCR results
    return ocr_results


if __name__ == "__main__":

    # Example usage
    image = cv2.imread(
        "src/scripts/image.jpg"
    )  # Replace this with your NumPy array input
    image_array = np.array(image)
    ocr_output = process_image(image_array)
    print("............")
    print(ocr_output)

    # Load image
    # image_path = "data/sample_image.jpg"
    # image = cv2.imread(image_path)

    # # Process image
    # ocr_results = process_image(image)
    # print(ocr_results)
