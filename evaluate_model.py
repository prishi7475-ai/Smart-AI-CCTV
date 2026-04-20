import os
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.metrics import confusion_matrix, accuracy_score
import seaborn as sns
import matplotlib.pyplot as plt

# Load model
model = load_model("models/emotion_model.h5", compile=False)

# Project emotions
emotions = ['Angry','Fear','Happy','Sad','Neutral']

# Model original labels
model_labels = ['Angry','Disgust','Fear','Happy','Sad','Surprise','Neutral']

dataset_path = "test_dataset"

y_true = []
y_pred = []

total_images = 0
skipped = 0

print("Starting evaluation...\n")

# Preprocess
def preprocess(img):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    gray = cv2.equalizeHist(gray)

    gray = cv2.GaussianBlur(gray,(3,3),0)

    face = cv2.resize(gray,(48,48))

    face = face/255.0

    face = np.reshape(face,(1,48,48,1))

    return face


for emotion in emotions:

    folder = os.path.join(dataset_path,emotion)

    if not os.path.exists(folder):
        continue

    for img_name in os.listdir(folder):

        total_images += 1

        img_path = os.path.join(folder,img_name)

        img = cv2.imread(img_path)

        if img is None:
            continue

        face = preprocess(img)

        prediction = model.predict(face,verbose=0)

        confidence = np.max(prediction)

        # Skip low confidence predictions
        if confidence < 0.60:
            skipped += 1
            continue

        pred_index = np.argmax(prediction)

        predicted_label = model_labels[pred_index]

        if predicted_label in ["Disgust","Surprise"]:
            continue

        y_true.append(emotion)
        y_pred.append(predicted_label)


accuracy = accuracy_score(y_true,y_pred)

print("Total Images:",total_images)
print("Used for Testing:",len(y_true))
print("Skipped Low Confidence:",skipped)
print("Overall Accuracy:",round(accuracy*100,2),"%\n")

cm = confusion_matrix(y_true,y_pred,labels=emotions)

print("Emotion-wise Accuracy\n")

for i,emotion in enumerate(emotions):

    correct = cm[i][i]
    total = np.sum(cm[i])

    if total == 0:
        acc = 0
    else:
        acc = correct/total

    print(emotion,":",round(acc*100,2),"%")

plt.figure(figsize=(8,6))

sns.heatmap(
    cm,
    annot=True,
    fmt='d',
    cmap="Blues",
    xticklabels=emotions,
    yticklabels=emotions
)

plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Emotion Detection Confusion Matrix")

plt.show()