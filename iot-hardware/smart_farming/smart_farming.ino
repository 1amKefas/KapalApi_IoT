#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>

// DHT22 setup
#define DHTPIN 4
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);

// LCD I2C address
LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  lcd.init();
  lcd.backlight();

  dht.begin();

  lcd.setCursor(0, 0);
  lcd.print("DHT22 Sensor");
  
  delay(2000);
  lcd.clear();
}

void loop() {

  float temp = dht.readTemperature();
  float hum  = dht.readHumidity();

  // Error check
  if (isnan(temp) || isnan(hum)) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Sensor Error");
    delay(2000);
    return;
  }

  lcd.clear();

  // Temperature
  lcd.setCursor(0, 0);
  lcd.print("Temp: ");
  lcd.print(temp, 1);
  lcd.print((char)223);
  lcd.print("C");

  // Humidity
  lcd.setCursor(0, 1);
  lcd.print("Hum : ");
  lcd.print(hum, 1);
  lcd.print("%");

  delay(2000);
}