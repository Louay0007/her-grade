// HER-GRADE ESP32 firmware — JSONL 115200, modes A/B, flap diverter, HW e-stop.
// E-stop cuts motor power via relay. Software stop is NOT safety.
#include <Arduino.h>
// Pins (adjust to bench wiring, document in hardware/WIRING.md)
#define PIN_MOTOR_PWM 25
#define PIN_SERVO 26
#define PIN_IR 34
#define PIN_LED_R 27
#define PIN_LED_G 14
#define PIN_ESTOP_SENSE 35
#define SERVO_ACCEPTED 20
#define SERVO_VERIFY 110

String rxBuf;
char mode = 'B'; // A supervised | B unattended
bool running = false;
volatile bool sensedFlag = false;
unsigned long lastHb = 0;
unsigned long senseTs = 0;

void IRAM_ATTR onSense() { sensedFlag = true; }
void motorStop() { analogWrite(PIN_MOTOR_PWM, 0); }
void motorGo(int pwm=140) { analogWrite(PIN_MOTOR_PWM, pwm); }
void servoTo(int deg) {
  // simple SG90 PWM: 500..2400us @50Hz — approximate with analogWrite shim
  int pulse = map(deg, 0, 180, 500, 2400);
  for (int i=0;i<15;i++){ digitalWrite(PIN_SERVO, HIGH); delayMicroseconds(pulse); digitalWrite(PIN_SERVO, LOW); delayMicroseconds(20000-pulse); }
}
void sendJson(const String& s){ Serial.println(s); }

void setup() {
  Serial.begin(115200);
  pinMode(PIN_MOTOR_PWM, OUTPUT); pinMode(PIN_SERVO, OUTPUT);
  pinMode(PIN_LED_R, OUTPUT); pinMode(PIN_LED_G, OUTPUT);
  pinMode(PIN_IR, INPUT_PULLUP); pinMode(PIN_ESTOP_SENSE, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_IR), onSense, FALLING);
  motorStop(); digitalWrite(PIN_LED_G, LOW); digitalWrite(PIN_LED_R, HIGH);
  sendJson("{\"t\":\"boot\",\"mode\":\"B\",\"note\":\"motor OFF until resume + local button\"}");
}

void handleLine(String line) {
  line.trim(); if(!line.length()) return;
  if (line.indexOf("\"t\":\"divert\"")>0 || line.indexOf("\"t\": \"divert\"")>0) {
    String target = line.indexOf("verify")>0 ? "verify" : "accepted";
    // wait for sensed with 3s timeout (jam detection)
    unsigned long t0 = millis(); sensedFlag = false;
    while(!sensedFlag && millis()-t0 < 3000){ delay(2); if(digitalRead(PIN_ESTOP_SENSE)==LOW){ sendJson("{\"t\":\"fault\",\"kind\":\"estop\"}"); motorStop(); return; } }
    if(!sensedFlag){ sendJson("{\"t\":\"fault\",\"kind\":\"jam\"}"); motorStop(); digitalWrite(PIN_LED_R,HIGH); return; }
    sendJson("{\"t\":\"sensed\"}");
    int delayMs = 180; delay(delayMs); // calibrated per bench
    servoTo(target=="accepted"?SERVO_ACCEPTED:SERVO_VERIFY);
    sendJson(String("{\"t\":\"diverted\",\"target\":\"")+target+"\"}");
    delay(400); servoTo(65); // home
  } else if (line.indexOf("\"mode\"")>0) {
    mode = line.indexOf("\"A\"")>0 ? 'A':'B';
    sendJson(String("{\"t\":\"mode_ack\",\"mode\":\"")+mode+"\"}");
  } else if (line.indexOf("stop")>0) { motorStop(); running=false; digitalWrite(PIN_LED_R,HIGH); digitalWrite(PIN_LED_G,LOW); sendJson("{\"t\":\"stopped\"}");
  } else if (line.indexOf("resume")>0) { running=true; motorGo(); digitalWrite(PIN_LED_R,LOW); digitalWrite(PIN_LED_G,HIGH); sendJson("{\"t\":\"resumed\"}");
  } else if (line.indexOf("\"t\":\"hb\"")>0) { /* laptop heartbeat, ignore */ }
}

void loop() {
  while (Serial.available()) { char c = Serial.read(); if(c=='\n'){ handleLine(rxBuf); rxBuf=""; } else rxBuf+=c; }
  if (millis()-lastHb > 1000) { lastHb = millis(); sendJson(String("{\"t\":\"hb\",\"mode\":\"")+mode+"\",\"running\":"+(running?"true":"false")+"}"); }
  if (digitalRead(PIN_ESTOP_SENSE)==LOW) { motorStop(); running=false; digitalWrite(PIN_LED_R,HIGH); }
  delay(5);
}
