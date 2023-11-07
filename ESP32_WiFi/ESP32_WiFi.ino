#define BLYNK_TEMPLATE_ID "TMPL3h8D24614"
#define BLYNK_TEMPLATE_NAME "Mohit"
#define BLYNK_AUTH_TOKEN "SqvDfNATRKHatr_ffczhmjGUdjvl_omB"

#include <WiFi.h>
#include <BlynkSimpleEsp32.h>

char auth[] = BLYNK_AUTH_TOKEN; // Your Blynk Auth Token
char ssid[] = "rizzler"; // Your Wi-Fi network SSID
char pass[] = "12345678"; // Your Wi-Fi network password

const int vibrationPin = 35;
const int gasPin = 32;

BlynkTimer timer;

void setup() {
  Serial.begin(115200);
  Blynk.begin(auth, ssid, pass);
  timer.setInterval(4000L, sendSensorData); // Send sensor data every 4 seconds
}

void loop() {
  Blynk.run();
  timer.run();
}

void sendSensorData() {
  int sensorValue = analogRead(vibrationPin);
  Blynk.virtualWrite(V1, sensorValue); // Assuming you have a Gauge widget on V1 in your Blynk app

  int gasState = analogRead(gasPin);
  Blynk.virtualWrite(V2, gasState); // Assuming you have a LED widget on V2 in your Blynk app
}
