import cv2
import requests
import time
import threading
from ultralytics import YOLO

# ==========================================
# 1. SETUP MODEL (BALIK KE .PT ASLI)
# ==========================================
# Pake file best.pt hasil training V2 kalian yang paling pintar!
model = YOLO('best.pt') 
API_URL = "http://localhost:8000/api/vision" # Ganti IP Kefas!
CAMERA_URL = "http://192.168.1.5:8080/video"

latest_frame = None
latest_boxes = []
tomato_counts = {'mentah': 0, 'mengkal': 0, 'matang': 0}
is_running = True

# ==========================================
# 2. PEKERJA 2 (THREAD AI) 
# ==========================================
def ai_worker():
    global latest_frame, latest_boxes, tomato_counts, is_running
    
    while is_running:
        if latest_frame is not None:
            frame_to_process = latest_frame.copy()
            
            # KUNCI AKURASI: conf dibalikin ke 0.5, imgsz naikin dikit ke 480
            # Biar tomat nggak ngeblur dan AI nggak gampang halusinasi!
            results = model(frame_to_process, conf=0.5, imgsz=480, verbose=False)
            
            temp_boxes = []
            temp_counts = {'mentah': 0, 'mengkal': 0, 'matang': 0}
            
            for r in results:
                for box in r.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cls_id = int(box.cls[0])
                    cls_name = model.names[cls_id].lower()
                    
                    temp_boxes.append((x1, y1, x2, y2, cls_name))
                    
                    if cls_name in ['mentah', 'raw']: temp_counts['mentah'] += 1
                    elif cls_name in ['mengkal', 'partially_ripe']: temp_counts['mengkal'] += 1
                    elif cls_name in ['matang', 'ripe']: temp_counts['matang'] += 1
                    
            latest_boxes = temp_boxes
            tomato_counts = temp_counts
            
        # Biarkan CPU narik nafas sebentar biar laptop nggak overheat
        time.sleep(0.05) 

ai_thread = threading.Thread(target=ai_worker)
ai_thread.start()

# ==========================================
# 3. PEKERJA 1 (VIDEO STREAM)
# ==========================================
cap = cv2.VideoCapture(CAMERA_URL)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

last_sent_time = time.time()
send_interval = 3 

print("Sistem Anti-Halusinasi Aktif! Tekan 'q' untuk keluar.")

while True:
    success, frame = cap.read()
    if not success:
        print("Kamera HP terputus! Cek koneksi WiFi.")
        break
        
    latest_frame = frame
    display_frame = frame.copy()
    
    # Render kotak dari memori AI terakhir
    for (x1, y1, x2, y2, cls_name) in latest_boxes:
        if cls_name in ['mentah', 'raw']: 
            color = (0, 255, 0)
        elif cls_name in ['mengkal', 'partially_ripe']: 
            color = (0, 165, 255)
        else: 
            color = (0, 0, 255)
            
        cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(display_frame, cls_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
    cv2.imshow("AI Vision (ASYNC)", display_frame)
    
    # ==========================================
    # 4. KIRIM DATA KE LARAVEL
    # ==========================================
    current_time = time.time()
    if current_time - last_sent_time >= send_interval:
        payload = {
            "raw_count": tomato_counts['mentah'],
            "partially_ripe_count": tomato_counts['mengkal'],
            "ripe_count": tomato_counts['matang']
        }
        try:
            requests.post(API_URL, json=payload, timeout=1)
            print(f"[{time.strftime('%H:%M:%S')}] OK! Dikirim: {payload}")
        except:
            pass 
        last_sent_time = current_time

    if cv2.waitKey(1) & 0xFF == ord('q'):
        is_running = False
        break

cap.release()
cv2.destroyAllWindows()
ai_thread.join()