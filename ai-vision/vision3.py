import cv2
import requests
import time
import threading
from ultralytics import YOLO

# ==========================================
# 1. SETUP MODEL
# ==========================================
model = YOLO('best(2).pt') 
API_URL = "http://localhost:8000/api/vision" # Ganti IP Kefas!
CAMERA_URL = "http://10.24.40.96:8080/video"

latest_frame = None
latest_boxes = []
tomato_counts = {'mentah': 0, 'mengkal': 0, 'matang': 0}
is_running = True

# ==========================================
# 2. KELAS PENYEDOT VIDEO (THE BUFFER KILLER)
# Ini rahasia biar videonya gak patah-patah!
# ==========================================
class VideoStream:
    def __init__(self, url):
        self.cap = cv2.VideoCapture(url)
        self.ret, self.frame = self.cap.read()
        self.running = True
        # Bikin pekerja khusus yang nyedot video doang
        self.thread = threading.Thread(target=self.update, daemon=True)
        self.thread.start()

    def update(self):
        while self.running:
            # Terus-terusan sedot frame secepat mungkin
            # Biar gak ada antrean (buffer) yang bikin freeze
            self.ret, self.frame = self.cap.read()

    def read(self):
        return self.ret, self.frame

    def stop(self):
        self.running = False
        self.thread.join()
        self.cap.release()

# ==========================================
# 3. PEKERJA 2 (THREAD AI) 
# ==========================================
def ai_worker():
    global latest_frame, latest_boxes, tomato_counts, is_running
    
    while is_running:
        if latest_frame is not None:
            frame_to_process = latest_frame.copy()
            
            results = model(frame_to_process, conf=0.5, imgsz=480, verbose=False)
            
            temp_boxes = []
            temp_counts = {'mentah': 0, 'mengkal': 0, 'matang': 0}
            
            for r in results:
                for box in r.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cls_id = int(box.cls[0])
                    cls_name = model.names[cls_id].lower()
                    
                    # INI DIA: Ambil angka persentase akurasi (Confidence)
                    conf = float(box.conf[0])
                    # Format jadi teks (Contoh: "matang 85%")
                    label_text = f"{cls_name} {int(conf * 100)}%"
                    
                    temp_boxes.append((x1, y1, x2, y2, label_text, cls_name))
                    
                    if cls_name in ['mentah', 'raw']: temp_counts['mentah'] += 1
                    elif cls_name in ['mengkal', 'partially_ripe']: temp_counts['mengkal'] += 1
                    elif cls_name in ['matang', 'ripe']: temp_counts['matang'] += 1
                    
            latest_boxes = temp_boxes
            tomato_counts = temp_counts
            
        time.sleep(0.01) 

ai_thread = threading.Thread(target=ai_worker, daemon=True)
ai_thread.start()

# ==========================================
# 4. MAIN THREAD (TAMPILAN)
# ==========================================
print("Sistem Super Anti-Lag Aktif! Tekan 'q' untuk keluar.")
stream = VideoStream(CAMERA_URL)

last_sent_time = time.time()
send_interval = 15 

while True:
    success, frame = stream.read()
    if not success:
        continue
        
    latest_frame = frame
    display_frame = frame.copy()
    
    # Render kotak dan label lengkap dengan persentasenya
    for (x1, y1, x2, y2, label_text, cls_name) in latest_boxes:
        if cls_name in ['mentah', 'raw']: 
            color = (0, 255, 0)
        elif cls_name in ['mengkal', 'partially_ripe']: 
            color = (0, 165, 255)
        else: 
            color = (0, 0, 255)
            
        cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, 2)
        # Nampilin teksnya (sekarang udah ada angkanya!)
        cv2.putText(display_frame, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
    cv2.imshow("AI Vision (ASYNC)", display_frame)
    
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

stream.stop()
cv2.destroyAllWindows()