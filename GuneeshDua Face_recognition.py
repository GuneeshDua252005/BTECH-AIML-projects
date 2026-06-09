import cv2
import numpy as np
import os
from sklearn.neighbors import KNeighborsClassifier

# Specify the dataset path
dataset_path = "./face_data"  # Path to folder containing .npy files with face data

# Ensure the dataset path exists
if not os.path.exists(dataset_path):
    print(f"Directory {dataset_path} not found. Please add .npy files with face data into this directory.")
    exit()

# Function to load face data
def load_face_data(dataset_path):
    face_data = []
    labels = []
    label_map = {}
    label_id = 0

    # Load each face data file
    for file_name in os.listdir(dataset_path):
        if file_name.endswith('.npy'):
            data = np.load(os.path.join(dataset_path, file_name))
            name = file_name.split('_face_data.npy')[0]  # Extract name from filename
            
            # Flatten faces and append data and labels
            for face in data:
                face_flattened = face.flatten()  # Flatten the face image into a 1D array
                face_data.append(face_flattened)
                labels.append(label_id)

            # Store the label for the person
            label_map[label_id] = name
            label_id += 1

    if len(face_data) == 0:
        print("No face data files found. Please add .npy files with face data.")
        exit()

    # Convert face data and labels to numpy arrays
    face_data = np.array(face_data)
    labels = np.array(labels)
    return face_data, labels, label_map

# Load data
face_data, labels, label_map = load_face_data(dataset_path)

# Train KNN classifier
knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(face_data, labels)

# Load Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
face_size = (100, 100)

# Start webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not access the webcam.")
    exit()

print("Press 'G' to exit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame")
        continue

    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        # Extract and resize the face from the frame
        face = frame[y:y+h, x:x+w]
        face_resized = cv2.resize(face, face_size)
        face_flattened = face_resized.flatten().reshape(1, -1)

        # Predict the person's label (ID)
        label = knn.predict(face_flattened)[0]
        name = label_map[label]  # Map the label to the person's name

        # Draw rectangle around face and add the name
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # Display the frame with the recognized face and name
    cv2.imshow("Face Recognition", frame)

    # Exit the loop if the user presses 'q'
    if cv2.waitKey(1) & 0xFF == ord('G'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
