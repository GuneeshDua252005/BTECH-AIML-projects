import cv2
import numpy as np
import os

# Set up the dataset path and person name
dataset_path = "./face_data"
person_name = "Guneesh Dua"  # Replace with the person's name
face_size = (100, 100)      # Resize face images to this size

# Ensure dataset path exists
os.makedirs(dataset_path, exist_ok=True)

# Initialize video capture and face detector
cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

face_data = []  # List to store face images

print("Press 'G' to stop capturing face data.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture image.")
        continue

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray_frame, 1.3, 5)

    for (x, y, w, h) in faces:
        # Draw a rectangle around the detected face
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # Extract the face region, resize, and save
        face = frame[y:y+h, x:x+w]
        face_resized = cv2.resize(face, face_size)
        face_data.append(face_resized)

    # Display the video feed with the rectangle drawn around faces
    cv2.imshow("Face Capture", frame)

    # Exit on pressing 'G'
    if cv2.waitKey(1) & 0xFF == ord('G'):
        break

# Release the video capture object and close windows
cap.release()
cv2.destroyAllWindows()

# Convert the list of faces to a numpy array and save it as .npy
person_name = "Guneesh Dua"  # Define the name without parentheses
file_path = os.path.join(dataset_path, f"{person_name}_face_data.npy")
np.save(file_path, face_data)
print(f"Face data for {person_name} saved to {file_path}.")