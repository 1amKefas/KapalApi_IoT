# KapalApi IoT - Smart Farming System

Sistem pemantauan pertanian pintar yang mengintegrasikan IoT (ESP32) dan AI Computer Vision (YOLOv8) untuk mendeteksi kematangan tomat dan mengontrol penyiraman otomatis.

## Cara Menjalankan Sistem
1. **Backend API (Laravel):** Masuk ke `backend-api`, jalankan `composer install`, setup `.env`, lalu `php artisan serve --host=0.0.0.0`.
2. **Frontend (SolidJS):** Masuk ke `smart-farming-dashboard`, jalankan `npm install`, lalu `npm run dev`.
3. **AI Vision (Python):** Masuk ke `ai-vision`, letakkan file `best.pt`, install requirements, lalu jalankan `python vision.py`.
4. **IoT Node (ESP32):** Buka folder `iot-hardware`, flash `smart_farming.ino` ke board ESP32 menggunakan Arduino IDE.