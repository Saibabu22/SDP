import streamlit as st
import cv2
from ultralytics import YOLO
from PIL import Image
from transformers import pipeline
import numpy as np
import tempfile

# Load YOLO Model
yolo_model = YOLO("yolov8n.pt")  # Pre-trained YOLOv8 model

# Load Face Comparison Model (Hugging Face)
face_recognition_model = pipeline("feature-extraction", model="openai/clip-vit-base-patch32")

def extract_frames(video_path, interval=30):
    """Extract frames from a video at a regular interval."""
    video = cv2.VideoCapture(video_path)
    frames = []
    count = 0

    while True:
        ret, frame = video.read()
        if not ret:
            break
        if count % interval == 0:
            frames.append(frame)
        count += 1

    video.release()
    return frames

def detect_mobile_in_frames(frames):
    """Detect mobile phones in video frames."""
    for frame in frames:
        results = yolo_model(frame)
        for result in results:
            if 'cell phone' in result.names:
                return True
    return False

def extract_face_embedding(image_path):
    """Extract face embedding from an image."""
    image = Image.open(image_path).convert("RGB")
    embedding = np.array(face_recognition_model(image)).mean(axis=1)
    return embedding

def match_faces(image_embedding, video_frames):
    """Match face from the uploaded image to faces in video frames."""
    for frame in video_frames:
        # Convert frame to PIL Image for processing
        frame_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        frame_embedding = np.array(face_recognition_model(frame_image)).mean(axis=1)
        similarity = np.dot(image_embedding, frame_embedding.T) / (
            np.linalg.norm(image_embedding) * np.linalg.norm(frame_embedding)
        )
        if similarity > 0.9:  # Threshold for similarity
            return True
    return False

# Streamlit App
st.title("Video Analysis App")
st.write("""
This application checks:
1. Whether a mobile phone is present in the video.
2. If the uploaded image matches any face in the video.
""")

# File Uploads
video_file = st.file_uploader("Upload Video File", type=["mp4", "avi", "mov"])
image_file = st.file_uploader("Upload Image File", type=["jpg", "jpeg", "png"])

if st.button("Analyze") and video_file and image_file:
    with st.spinner("Processing video..."):
        # Save video to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_video:
            temp_video.write(video_file.read())
            video_path = temp_video.name

        # Save image to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_image:
            temp_image.write(image_file.read())
            image_path = temp_image.name

        # Extract frames from video
        st.write("Extracting frames from the video...")
        frames = extract_frames(video_path)

        # Detect mobile phone in frames
        st.write("Checking for mobile phones in the video...")
        mobile_present = detect_mobile_in_frames(frames)
        if mobile_present:
            st.success("Mobile phone detected in the video!")
        else:
            st.info("No mobile phone detected in the video.")

        # Extract face embedding from uploaded image
        st.write("Analyzing the uploaded image...")
        image_embedding = extract_face_embedding(image_path)

        # Match faces between the image and video
        st.write("Matching the uploaded image with faces in the video...")
        face_matched = match_faces(image_embedding, frames)
        if face_matched:
            st.success("The uploaded image matches a face in the video!")
        else:
            st.info("The uploaded image does not match any face in the video.")
