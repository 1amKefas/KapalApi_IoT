#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

// ==========================================
// 1. PENGATURAN WIFI & API
// ==========================================
const char* ssid = "NAMA_WIFI_KALIAN";
const char* password = "PASSWORD_WIFI";
// Ganti X dengan IP Address laptop lu (Kefas)
const char* serverName = "http://192.168.1.X:8000/api/sensor"; 

// ==========================================
// 2. PENGATURAN PIN SENSOR (Sesuaikan nanti dengan wiring Rigin)
// ==========================================
#define DHTPIN 4          // Pin data DHT22 nyambung ke GPIO 4
#define DHTTYPE DHT22     // Jenis sensor DHT
#define SOIL_PIN 34       // Pin analog sensor kelembapan tanah (A0)
#define RELAY_PIN 5       // Pin untuk modul relay pompa air

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  
  // Inisialisasi Sensor & Pin
  dht.begin();
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, HIGH); // Asumsi relay aktif LOW (HIGH = Pompa Mati)

  // Koneksi ke WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected!");
}

void loop() {
  if(WiFi.status() == WL_CONNECTED) {
    // --- A. BACA SENSOR UDARA ---
    float humidity = dht.readHumidity();
    float temperature = dht.readTemperature();
    
    // Cek kalau sensor DHT gagal kebaca
    if (isnan(humidity) || isnan(temperature)) {
      Serial.println("Gagal membaca dari sensor DHT!");
      temperature = 0; humidity = 0;
    }

    // --- B. BACA SENSOR TANAH ---
    // ESP32 punya ADC 12-bit (0 - 4095). 
    // Asumsi: 4095 = Kering kerontang, 0 = Tenggelam air. (Nanti perlu dikalibrasi Rigin)
    int soilAnalog = analogRead(SOIL_PIN);
    float soilMoisture = map(soilAnalog, 4095, 0, 0, 100);
    
    // Batasi nilai persentase biar gak error nampil di UI
    if(soilMoisture < 0) soilMoisture = 0;
    if(soilMoisture > 100) soilMoisture = 100;

    // --- C. LOGIKA POMPA OTOMATIS ---
    bool pumpStatus = false;
    if (soilMoisture < 40.0) { 
      // Kalau tanah kering (< 40%), nyalain pompa
      digitalWrite(RELAY_PIN, LOW); // Relay Aktif
      pumpStatus = true;
    } else {
      // Kalau udah basah, matiin
      digitalWrite(RELAY_PIN, HIGH);
      pumpStatus = false;
    }

    // --- D. KIRIM DATA KE LARAVEL API ---
    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");

    // Rakit string JSON sesuai atribut tabel "sensor_logs" lu
    String jsonPayload = "{";
    jsonPayload += "\"temperature\": " + String(temperature) + ",";
    jsonPayload += "\"air_humidity\": " + String(humidity) + ",";
    jsonPayload += "\"soil_moisture\": " + String(soilMoisture) + ",";
    jsonPayload += "\"pump_status\": " + String(pumpStatus ? "true" : "false");
    jsonPayload += "}";

    int httpResponseCode = http.POST(jsonPayload);
    
    Serial.print("Data dikirim: ");
    Serial.println(jsonPayload);
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);
    
    http.end();
  } else {
    Serial.println("WiFi Disconnected");
  }
  
  // Kirim data setiap 5 detik
  delay(5000); 
}