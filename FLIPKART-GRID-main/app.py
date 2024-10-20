from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt
from src.controller.analyze_image import imageResults

app = Flask(__name__)
socketio = SocketIO(app)


# Default route
@app.route("/")
def index():
    return render_template("index.html")


# Route to serve the camera feed page
@app.route("/detect")
def detect():
    return render_template("detect.html")


# Route to serve the results page
@app.route("/results")
def results():
    return render_template("results.html")


# Route to handle image analysis
@app.route("/analyze", methods=["POST"])
def analyze_image():
    # Get the base64 image string from the request
    image_data = request.form.get("image")
    image = Image.open(BytesIO(base64.b64decode(image_data.split(",")[1])))

    # Convert image to OpenCV format
    opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Save image to disk
    cv2.imwrite("image.jpg", opencv_image)

    image_array = np.array(image)

    # Perform image analysis
    print("Performing image analysis...")
    # Get the results of the image analysis
    results = imageResults(image_array)
    print(type(results))
    print(results)

    # # For demo purposes, let's assume we detected "object"
    # detected_objects = ["Object Detected"]

    # Send results to results page via WebSocket
    # socketio.emit("results_channel", {"objects": detected_objects})

    socketio.emit("results_channel", {"objects": results})

    return jsonify({"status": "Image received and analyzed"})


if __name__ == "__main__":
    socketio.run(app, debug=True, port=3100)
