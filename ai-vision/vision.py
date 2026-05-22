import cv2
import requests
import time
import torch
from ultralytics import YOLO

# ==========================================
# 1. SETUP MODEL & API
# ==========================================
# Load model YOLOv8 (pastikan best(2).pt ada di folder yang sama!)
# Select device: use GPU if available
device = "cuda:0" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Load the .pt model (replace with .onnx only if you need the ONNX runtime)
model = YOLO('best(2).pt')


# Endpoint API Laravel Kefas
API_URL = "http://localhost:8000/api/vision"

# ==========================================
# 2. SETUP KAMERA
# ==========================================
# Pakai 0 untuk webcam bawaan laptop. 
#cap = cv2.VideoCapture(0)

# IP Webcam
cap = cv2.VideoCapture("http://10.24.40.96:8080/video")

# Turunin resolusi kamera dasar biar nggak berat di CPU
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Atur biar ngirim data ke database tiap 3 detik aja biar ga jebol servernya
last_sent_time = time.time()
send_interval = 3 

print("Mulai membaca kamera... Tekan 'q' untuk berhenti.")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Gagal membaca frame kamera.")
        break

    # ==========================================
    # 3. PROSES DETEKSI AI YOLOv8
    # ==========================================
    # conf=0.6 -> Hanya deteksi kalau AI yakin 60% ke atas! (Muka lu aman)
    # imgsz=480 -> Bikin proses nebak di CPU laptop jauh lebih enteng!
    results = model(frame, stream=True, conf=0.6, imgsz=480, device=device)

    # Siapkan wadah jumlah tomat
    tomato_counts = {'mentah': 0, 'mengkal': 0, 'matang': 0}

    annotated_frame = frame

    for r in results:
        boxes = r.boxes
        for box in boxes:
            # Ambil nama kelas yang terdeteksi
            cls_id = int(box.cls[0])
            cls_name = model.names[cls_id].lower()

            # Hitung jumlahnya (sesuaikan dengan nama class di Roboflow kalian)
            if cls_name == 'mentah' or cls_name == 'raw':
                tomato_counts['mentah'] += 1
            elif cls_name == 'mengkal' or cls_name == 'partially_ripe':
                tomato_counts['mengkal'] += 1
            elif cls_name == 'matang' or cls_name == 'ripe':
                tomato_counts['matang'] += 1

        # Gambar bounding box di video
        annotated_frame = r.plot()

    # Tampilkan video ke layar Mufti
    cv2.imshow("AI Vision - Smart Farming", annotated_frame)

    # ==========================================
    # 4. KIRIM DATA KE API
    # ==========================================
    current_time = time.time()
    if current_time - last_sent_time >= send_interval:
        # Format data JSON yang diminta sama API Laravel
        payload = {
            "raw_count": tomato_counts['mentah'],
            "partially_ripe_count": tomato_counts['mengkal'],
            "ripe_count": tomato_counts['matang']
        }

        try:
            # Tembak POST Request
            response = requests.post(API_URL, json=payload, timeout=3)
            print(f"[{time.strftime('%H:%M:%S')}] OK! Deteksi dikirim: {payload}")
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] Gagal kirim ke API. Cek IP/koneksi Laravel.")
        
        last_sent_time = current_time

    # Tekan 'q' buat close
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()