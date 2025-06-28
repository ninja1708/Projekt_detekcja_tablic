from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QFileDialog, QDialog, QDialogButtonBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import threading
from main import detect_and_read_license_plate, CameraHandler
import cv2

class LicensePlateApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("License Plate Recognition")
        self.setGeometry(100, 100, 800, 600)
        self.initUI()
        self.camera_handler = CameraHandler()
        self.camera_thread = None
        self.running = False

    def initUI(self):
        main_layout = QVBoxLayout()

        top_layout = QHBoxLayout()


        self.image_label = QLabel("Brak obrazu")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid black; background-color: white;")
        top_layout.addWidget(self.image_label, stretch=2)

        # Prawa strona - logo i kontrolki
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignTop)

        self.logo_label = QLabel()
        pixmap_logo = QPixmap('logo.png')
        self.logo_label.setPixmap(pixmap_logo.scaled(200, 100, Qt.KeepAspectRatio))
        self.logo_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        right_layout.addWidget(self.logo_label)

        self.result_label = QLabel("Wykryta rejestracja: ")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        right_layout.addWidget(self.result_label)

        self.comment_label = QLabel("Komentarz: ")
        self.comment_label.setAlignment(Qt.AlignCenter)
        self.comment_label.setStyleSheet("font-size: 16px; color: grey; border-top: 1px solid black;")
        right_layout.addWidget(self.comment_label)

        self.source_button = QPushButton("Wybierz źródło obrazu")
        self.source_button.clicked.connect(self.select_source)
        right_layout.addWidget(self.source_button)

        top_layout.addLayout(right_layout, stretch=1)

        main_layout.addLayout(top_layout)
        self.setLayout(main_layout)

    def select_source(self):
        self.stop_camera()
        dialog = QDialog(self)
        dialog.setWindowTitle("Wybierz źródło obrazu")
        layout = QVBoxLayout()

        camera_btn = QPushButton("Użyj kamery")
        camera_btn.clicked.connect(lambda: self.start_camera(dialog))
        layout.addWidget(camera_btn)

        image_btn = QPushButton("Wybierz obraz z pliku")
        image_btn.clicked.connect(lambda: self.load_image(dialog))
        layout.addWidget(image_btn)

        video_btn = QPushButton("Otwórz plik wideo")
        video_btn.clicked.connect(lambda: self.load_video_file(dialog))
        layout.addWidget(video_btn)

        buttons = QDialogButtonBox(QDialogButtonBox.Cancel)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        dialog.exec_()

    def load_image(self, dialog):
        dialog.accept()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            result, comment, processed_image = detect_and_read_license_plate(file_path)
            self.result_label.setText(f"Wykryta rejestracja: \n{result}")
            self.comment_label.setText(f"Komentarz: \n{comment}")
            if processed_image is not None:
                pixmap = QPixmap.fromImage(QImage(processed_image, processed_image.shape[1], processed_image.shape[0],
                                                  processed_image.strides[0], QImage.Format_RGB888))
                self.image_label.setPixmap(pixmap.scaled(600, 400, Qt.KeepAspectRatio))

    def load_video_file(self, dialog):
        dialog.accept()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Video", "", "Videos (*.mp4 *.avi *.mov)")
        if file_path:
            self.running = True
            self.camera_thread = threading.Thread(target=self.camera_handler.start_video_file,
                                                  args=(file_path, self.update_camera_feed))
            self.camera_thread.start()

    def start_camera(self, dialog):
        dialog.accept()
        self.running = True
        self.camera_thread = threading.Thread(target=self.camera_handler.start_camera,
                                              args=(self.update_camera_feed,))
        self.camera_thread.start()

    def stop_camera(self):
        if self.running:
            self.camera_handler.stop_camera()
            if self.camera_thread:
                self.camera_thread.join()
            self.running = False
            self.image_label.setText("Brak obrazu")

    def update_camera_feed(self, result, comment, frame):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = rgb_image.shape
        step = channel * width
        q_image = QImage(rgb_image.data, width, height, step, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(q_image).scaled(600, 400, Qt.KeepAspectRatio))
        self.result_label.setText(f"Wykryta rejestracja: \n{result}" if result else "Brak wykrycia")
        self.comment_label.setText(f"Komentarz: \n{comment}" if comment else "Brak komentarza")

    def closeEvent(self, event):
        self.stop_camera()
        super().closeEvent(event)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    main_window = LicensePlateApp()
    main_window.show()
    sys.exit(app.exec_())