import cv2
import requests
import time
import threading
from flask import Flask, Response
from ultralytics import YOLO

# Inisialisasi Mini Server
app = Flask(__name__)

# ==========================================
# 1. SETUP MODEL & API
# ==========================================
model = YOLO('best(2).pt') 
API_URL = "http://localhost:8000/api/vision" # Ganti IP Kefas!
CAMERA_URL = "http://10.21.136.5:8080/video"

latest_frame = None
latest_boxes = []
tomato_counts = {'mentah': 0, 'mengkal': 0, 'matang': 0}
is_running = True
display_frame = None # Wadah khusus buat dikirim ke SolidJS

# ==========================================
# 2. KELAS PENYEDOT VIDEO (Anti-Lag)
# ==========================================
class VideoStream:
    def __init__(self, url):
        self.cap = cv2.VideoCapture(url)
        self.ret, self.frame = self.cap.read()
        self.running = True
        self.thread = threading.Thread(target=self.update, daemon=True)
        self.thread.start()

    def update(self):
        while self.running:
            self.ret, self.frame = self.cap.read()

    def read(self):
        return self.ret, self.frame

    def stop(self):
        self.running = False
        self.thread.join()
        self.cap.release()

# ==========================================
# 3. PEKERJA 2 (THREAD AI MIKIR)
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
                    conf = float(box.conf[0])
                    label_text = f"{cls_name} {int(conf * 100)}%"
                    
                    temp_boxes.append((x1, y1, x2, y2, label_text, cls_name))
                    
                    if cls_name in ['mentah', 'raw']: temp_counts['mentah'] += 1
                    elif cls_name in ['mengkal', 'partially_ripe']: temp_counts['mengkal'] += 1
                    elif cls_name in ['matang', 'ripe']: temp_counts['matang'] += 1
                    
            latest_boxes = temp_boxes
            tomato_counts = temp_counts
            
        time.sleep(0.01) 

# ==========================================
# 4. PEKERJA PENGGAMBAR & PENGIRIM DATA
# ==========================================
def main_worker():
    global latest_frame, display_frame, is_running
    
    stream = VideoStream(CAMERA_URL)
    last_sent_time = time.time()
    send_interval = 15 # Kirim database per 15 detik
    
    while is_running:
        success, frame = stream.read()
        if not success:
            time.sleep(0.1)
            continue
            
        latest_frame = frame
        temp_display = frame.copy()
        
        # Gambar kotak AI
        for (x1, y1, x2, y2, label_text, cls_name) in latest_boxes:
            if cls_name in ['mentah', 'raw']: color = (0, 255, 0)
            elif cls_name in ['mengkal', 'partially_ripe']: color = (0, 165, 255)
            else: color = (0, 0, 255)
                
            cv2.rectangle(temp_display, (x1, y1), (x2, y2), color, 2)
            cv2.putText(temp_display, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
        # Simpan gambar yang udah dicoret ke variabel global buat disedot Flask
        display_frame = temp_display
        
        # Kirim API
        current_time = time.time()
        if current_time - last_sent_time >= send_interval:
            payload = {
                "raw_count": tomato_counts['mentah'],
                "partially_ripe_count": tomato_counts['mengkal'],
                "ripe_count": tomato_counts['matang']
            }
            try:
                requests.post(API_URL, json=payload, timeout=1)
                print(f"[{time.strftime('%H:%M:%S')}] OK! Data ke Laravel: {payload}")
            except:
                pass 
            last_sent_time = current_time
            
        time.sleep(0.01) 
        
    stream.stop()

# ==========================================
# 5. SERVER FLASK (JEMBATAN KE SOLIDJS)
# ==========================================
def generate_frames():
    global display_frame
    while is_running:
        if display_frame is not None:
            # Ubah frame OpenCV (Numpy Array) jadi format gambar JPEG
            ret, buffer = cv2.imencode('.jpg', display_frame)
            if ret:
                frame_bytes = buffer.tobytes()
                # Yield data ke dalam format streaming MJPEG
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.03) # Limit sekitar 30 FPS untuk web

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Nyalakan para pekerja di belakang layar
    threading.Thread(target=ai_worker, daemon=True).start()
    threading.Thread(target=main_worker, daemon=True).start()
    
    print("Membuka Server Streaming di Port 5000...")
    print("SolidJS sekarang bisa mengambil video dari: http://localhost:5000/video_feed")
    
    # Jalankan Flask (Web Server)
    app.run(host='0.0.0.0', port=5000, threaded=True, use_reloader=False)