import cv2
from ultralytics import YOLO
import easyocr
import numpy as np
import re
import time
import os
import random
from datetime import datetime
import sqlite3

model = YOLO('yolo_license_plate.pt')
reader = easyocr.Reader(['en', 'pl'])

if not os.path.exists("detections"):
    os.makedirs("detections")

def preprocess_plate(plate):
    gray = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    processed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    return processed

def postprocess_text(text):
    text = text.upper()
    text = re.sub('[^A-Z0-9]', '', text)
    if re.match(r'^[A-Z]{1,3}[0-9]{1,5}$', text):
        return text
    return text.replace('I', '1').replace('O', '0')

def detect_and_read_license_plate(image):
    if isinstance(image, str):
        image = cv2.imread(image)

    if image is None:
        print("Nie udało się wczytać obrazu.")
        return None, None, None

    results = model(image)
    detected_text = ""
    detection_made = False

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            plate = image[y1:y2, x1:x2]
            processed_plate = preprocess_plate(plate)
            ocr_result = reader.readtext(processed_plate)

            for (_, text, _) in ocr_result:
                detected_text = postprocess_text(text)
                detection_made = True

            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)


    comment = ""
    if detection_made:
        try:
            conn = sqlite3.connect('license_plates.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM authorized_plates WHERE plate_number = ?", (detected_text,))
            row = cursor.fetchone()

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if row:
                comment = "Tablica rozpoznana, zapraszam"
            else:
                comment = "Nie rozpoznano rejestracji, brak zezwolenia na wjazd"

            # Zapisz log
            try:
                cursor.execute(
                    "INSERT INTO detection_logs (timestamp, plate_number, comment) VALUES (?, ?, ?)",
                    (timestamp, detected_text, comment)
                )
                conn.commit()
            except Exception as log_error:
                print("Błąd zapisu logu:", log_error)

            conn.close()
        except Exception as e:
            print("Błąd bazy danych:", e)
            comment = "Błąd podczas sprawdzania bazy"

        timestamp_img = datetime.now().strftime('%Y%m%d_%H%M%S')
        cv2.imwrite(f"detections/detection_{timestamp_img}.jpg", image)

    q_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return detected_text, comment, q_image

class CameraHandler:
    def __init__(self):
        self.capture = None
        self.running = False

    def start_camera(self, callback):
        if self.running:
            return
        self.capture = cv2.VideoCapture(0)
        self.running = True
        self._camera_loop(callback)

    def start_video_file(self, video_path, callback):
        if self.running:
            return
        self.capture = cv2.VideoCapture(video_path)
        self.running = True
        self._camera_loop(callback)

    def _camera_loop(self, callback):
        last_detection_time = 0
        detection_delay = 3

        while self.running:
            ret, frame = self.capture.read()
            if not ret:
                break

            current_time = time.time()
            if current_time - last_detection_time > detection_delay:
                result, comment, processed_frame = detect_and_read_license_plate(frame)
                if result:
                    last_detection_time = current_time
                callback(result, comment, processed_frame)
            else:
                callback("", "", frame)

    def stop_camera(self):
        if self.running:
            self.running = False
            if self.capture:
                self.capture.release()
                self.capture = None
