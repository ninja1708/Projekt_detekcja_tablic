# Detekcja Tablic Rejestracyjnych z użyciem YOLOv8n

Projekt pokazowy demonstrujący wykorzystanie lekkiego modelu **YOLOv8n** (YOLOv8 Nano) do detekcji **tablic rejestracyjnych** na obrazach i nagraniach wideo. Model został wytrenowany na publicznie dostępnych zbiorach danych z platformy **Kaggle**.

## 🧠 Użyte Technologie

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics) (wersja `8n`)
- Python 3.10+
- PyTorch
- OpenCV
- Kaggle Datasets

## 📂 Struktura Projektu


## 🗃️ Zbiory Danych

Do nauki modelu wykorzystano publiczne zbiory danych z Kaggle zawierające obrazy pojazdów z oznaczonymi tablicami rejestracyjnymi (np. `Car License Plate Detection`, `Vehicle Number Plate Dataset`). Adnotacje zostały przekonwertowane do formatu YOLO.

## 🚀 Trening Modelu

Model został wytrenowany za pomocą polecenia:

```bash
yolo task=detect mode=train model=yolov8n.pt data=dataset.yaml epochs=50 imgsz=640
```
## Instalcaja bibliotek
```bash
pip install -r importy.txt
```
