const video = document.querySelector("#videoElement");
const captureButton = document.querySelector("#captureButton");
const timerCanvas = document.querySelector("#timerCanvas");
const ctx = timerCanvas.getContext("2d");
let detectionInterval = document.querySelector("#interval").value;
let intervalId;
let countdown;
let timeLeft;

// Function to resize the canvas to match the video size
function resizeCanvas() {
  timerCanvas.width = video.videoWidth;
  timerCanvas.height = video.videoHeight;
}

// Function to update the countdown display on the canvas
function updateTimerDisplay() {
  ctx.clearRect(0, 0, timerCanvas.width, timerCanvas.height); // Clear previous text
  ctx.font = "48px Arial";
  ctx.fillStyle = "white";
  ctx.textAlign = "center";
  ctx.fillText(timeLeft, timerCanvas.width / 2, 50); // Display time left at the top-center
}

// Function to show image capture effect (dim the video)
function showCaptureEffect() {
  video.style.filter = "brightness(0.5)";
  setTimeout(() => {
    video.style.filter = "brightness(1)";
  }, 100); // Reset after 100ms
}

// Function to start the automatic capture with a countdown
function startAutoCapture(interval) {
  clearInterval(intervalId); // Clear any previous intervals
  timeLeft = interval / 1000;

  intervalId = setInterval(() => {
    if (timeLeft === 0) {
      updateTimerDisplay();
      captureImageAndSend();
      showCaptureEffect(); // Simulate camera capture effect
      timeLeft = interval / 1000; // Reset countdown
    } else {
      updateTimerDisplay();
      timeLeft--; // Decrement timer
    }
  }, 1000);
}

// Function to stop the automatic capture
function stopAutoCapture() {
  clearInterval(intervalId);
  clearInterval(countdown);
  ctx.clearRect(0, 0, timerCanvas.width, timerCanvas.height); // Clear timer display
}

// Function to capture and send the image
function captureImageAndSend() {
  let canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  let ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  // Convert canvas to base64 image
  let imageData = canvas.toDataURL("image/png");

  // Send the image to the backend
  fetch("/analyze", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({ image: imageData }),
  })
    .then((response) => response.json())
    .then((data) => console.log("Image sent for analysis"));
}

// Access the camera
navigator.mediaDevices
  .getUserMedia({ video: true })
  .then(function (stream) {
    video.srcObject = stream;
    video.onloadedmetadata = function () {
      resizeCanvas(); // Resize the canvas when video metadata is loaded
    };
  })
  .catch(function (err) {
    console.log("Error accessing the camera: " + err);
  });

// Handle dropdown change event
document.querySelector("#interval").addEventListener("change", function () {
  detectionInterval = this.value;

  if (detectionInterval === "manual") {
    // Show the manual capture button and stop automatic capture
    captureButton.style.display = "block";
    stopAutoCapture();
  } else {
    // Hide the manual capture button and start automatic capture
    captureButton.style.display = "none";
    startAutoCapture(detectionInterval);
  }
});

// Handle manual capture button click
captureButton.addEventListener("click", function () {
  captureImageAndSend();
  showCaptureEffect(); // Show capture effect on manual capture
});

// Initialize automatic capture on page load if not in manual mode
if (detectionInterval !== "manual") {
  startAutoCapture(detectionInterval);
}

// Resize the canvas if the window is resized
window.addEventListener("resize", resizeCanvas);
