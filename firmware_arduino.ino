/*

Firmware Arduino
Desenvolvido por Thiago Barros

*/


#define PIN_LEFT   5
#define PIN_RIGHT  7
#define PIN_SPEED  8
#define PIN_LOW    10
#define PIN_HIGH   9

#define PIN_FUEL_LOW   11
#define PIN_FUEL_MED   12
#define PIN_FUEL_CRIT  13

int C = 0;
int B = 0;
int E = 0;

int L = 0;
int R = 0;

int LOW_BEAM = 0;
int HIGH_BEAM = 0;

int SPD_WARN = 0;

int F1 = 0;
int F2 = 0;
int F3 = 0;

// blink
bool blinkState = false;
unsigned long lastBlink = 0;
unsigned long blinkDelay = 250;

// =========================================================
void setup() {

    Serial.begin(115200);

    pinMode(PIN_LEFT, OUTPUT);
    pinMode(PIN_RIGHT, OUTPUT);
    pinMode(PIN_SPEED, OUTPUT);
    pinMode(PIN_LOW, OUTPUT);
    pinMode(PIN_HIGH, OUTPUT);

    pinMode(PIN_FUEL_LOW, OUTPUT);
    pinMode(PIN_FUEL_MED, OUTPUT);
    pinMode(PIN_FUEL_CRIT, OUTPUT);

    resetAll();
}

// =========================================================
void resetAll() {

    digitalWrite(PIN_LEFT, LOW);
    digitalWrite(PIN_RIGHT, LOW);
    digitalWrite(PIN_SPEED, LOW);
    digitalWrite(PIN_LOW, LOW);
    digitalWrite(PIN_HIGH, LOW);

    digitalWrite(PIN_FUEL_LOW, LOW);
    digitalWrite(PIN_FUEL_MED, LOW);
    digitalWrite(PIN_FUEL_CRIT, LOW);

    blinkState = false;
}

// =========================================================
void updateBlink() {

    if (millis() - lastBlink >= blinkDelay) {
        lastBlink = millis();
        blinkState = !blinkState;
    }
}

// =========================================================
void applyOutputs() {

    if (!C || !E) {
        resetAll();
        return;
    }

    updateBlink();

    bool hazard = (L && R);

    // SETAS
    if (hazard) {
        digitalWrite(PIN_LEFT, LOW);
        digitalWrite(PIN_RIGHT, LOW);
    } else {
        digitalWrite(PIN_LEFT, L ? blinkState : LOW);
        digitalWrite(PIN_RIGHT, R ? blinkState : LOW);
    }

    // SPEED
    digitalWrite(PIN_SPEED, SPD_WARN ? HIGH : LOW);

    // LUZES
    digitalWrite(PIN_LOW, LOW_BEAM ? HIGH : LOW);
    digitalWrite(PIN_HIGH, (HIGH_BEAM && LOW_BEAM) ? HIGH : LOW);

    // FUEL
    digitalWrite(PIN_FUEL_LOW, F1 ? HIGH : LOW);
    digitalWrite(PIN_FUEL_MED, F2 ? HIGH : LOW);
    digitalWrite(PIN_FUEL_CRIT, F3 ? HIGH : LOW);
}

// =========================================================
void loop() {

    if (Serial.available() < 12) return;

    if (Serial.read() != 0xAA) return;

    C = Serial.read();
    B = Serial.read();
    E = Serial.read();
    L = Serial.read();
    R = Serial.read();
    LOW_BEAM = Serial.read();
    HIGH_BEAM = Serial.read();
    SPD_WARN = Serial.read();

    F1 = Serial.read();
    F2 = Serial.read();
    F3 = Serial.read();

    applyOutputs();
}