#include <Servo.h>
#include <CAN.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
//#include <Math.h>

int thrusterPins[] = {5, 6, 9, 10, 11, 12, 13, 0};
int CAN_ID = 0x32;
// Q1diag, Q2diag, Q3diag, Q4diag, Q1up, Q2up, Q3up, Q4up
Servo thrusters[8];

bool enabledPid[4];

typedef struct PID{
  float pConstant;
  float iConstant;
  float dConstant;
  float targetVal;
  float totalError;
  float pastError;
  float* compareVal;
//  may be easier to just use current praseManualMoveCommand with PIDs
//  void(*outputFunc)(float);
//  float(*compareFunc)(float, float);
} pidc_t;

//BNO DATA
//float orientationEuler[3];
//float gyroData[3];
//float accelData[3];
sensors_event_t orientationData;
sensors_event_t gyroData;
sensors_event_t accelData;

//milliseconds
int imuUpdateDelay = 4;

unsigned long delayClock;
unsigned long lastImuUpdate;


//manual config
int manualSpeeds[6];

//pid stuff
bool pidEnabled = true;
bool gyroEnabled = true;
pidc_t pidF = {2.2, 3.4, 2.3, 0, 0};
pidc_t pidS = {2.2, 3.4, 2.3, 0, 0};
pidc_t pidU = {2.2, 3.4, 2.3, 0, 0};
pidc_t pidR = {2.2, 3.4, 2.3, 0, 0};
pidc_t pidP = {2.2, 3.4, 2.3, 0, 0};
pidc_t pidY = {2.2, 3.4, 2.3, 0, 0};
//pid using gyroscope
pidc_t pidRG = {2.2, 3.4, 2.3, 0, 0};
pidc_t pidPG = {2.2, 3.4, 2.3, 0, 0};
pidc_t pidYG = {2.2, 3.4, 2.3, 0, 0};

pidc_t* pidVals[] = {&pidF, &pidS, &pidU, &pidRG, &pidPG, &pidYG, &pidR, &pidP, &pidY};

Adafruit_BNO055 bno = Adafruit_BNO055(55);

unsigned long deltaTime;
unsigned long pastTime;

void setup() {
  for (int i = 0; i < 8; i++){
    thrusters[i].attach(thrusterPins[i]);
  }
  pastTime = millis();
//  begin can setup things
//  pinMode(PIN_CAN_SANDBY, OUTPUT);
//  digitalWrite(PIN_CAN_STANDBY, false); // what is standby?
//  pinMode(PIN_CAN_BOOSTEN, OUTPUT);
//  digitalWrite(PIN_CAN_BOOSTEN, true);
  CAN.begin(250000);
  bno.begin();
}

void loop() {
  unsigned long now = millis();
  deltaTime = now - pastTime;
  pastTime = now;
  updateSensorReadings();

  
  if (!pidEnabled){
    int test = manualSpeeds[0];
    parseManualMoveCommand(manualSpeeds[0], manualSpeeds[1], manualSpeeds[2], manualSpeeds[3], manualSpeeds[4], manualSpeeds[5]);
  }
  else{
    allPidLoop();
  }
  readCan();
  sendSensorData();
}

//updates sensor values, updates pid, and sends sensor data
void sensorUpdateLoop(){
  if (imuUpdateDelay != -1){
    
  }
}

void sendSensorData(){
  if(imuUpdateDelay != -1){
    delayClock -= deltaTime;
    if(delayClock < 0){
      delayClock += imuUpdateDelay;
      float val;
      for (int i = 0; i < 3; i++){
        for (int j = 0; j < 3; j++){
          switch(i){
            case 0:
              val = orientationData.data[j];
            break;
            case 1:
              val = gyroData.data[i];
            break;
            case 2:
              val = accelData.data[i];
            break;
          }
          CAN.beginPacket(i*3+j);
          CAN.write(((byte*)&val)[0]);
          CAN.write(((byte*)&val)[1]);
          CAN.write(((byte*)&val)[2]);
          CAN.write(((byte*)&val)[3]);
          CAN.endPacket();
        }
      }
    }
  }
}

void updateSensorReadings(){
//  sensors_event_t orientationEvent;
//  sensors_event_t accelerationEvent;
//  sensors_event_t gyroEvent;
//  bno.getEvent(&orientationEvent, Adafruit_BNO055::VECTOR_ACCELEROMETER);
//  bno.getEvent(&accelerationEvent);
//  bno.getEvent(&gyroEvent);
//  orientationEuler[0] = orientationEvent.orientation.x;
//  orientationEuler[1] = orientationEvent.orientation.y;
//  orientationEuler[2] = orientationEvent.orientation.z;
//  accelData[0] = accelerationEvent.acceleration.x;
//  accelData[1] = accelerationEvent.acceleration.y;
//  accelData[2] = accelerationEvent.acceleration.z;
//  gyroData[0] = gyroEvent.gyro.x;
//  gyroData[1] = gyroEvent.gyro.y;
//  gyroData[2] = gyroEvent.gyro.z;
  bno.getEvent(&orientationData, Adafruit_BNO055::VECTOR_ACCELEROMETER);
  bno.getEvent(&accelData);
  bno.getEvent(&gyroData);
}

bool readCan(){
  int packetSize = CAN.parsePacket();
  bool adjustPid = true;
  bool adjustManual = false;
  pidc_t *selectedPid;
  float value;
  if (packetSize > 0){
    if (CAN.packetId() == CAN_ID){
      switch(CAN.read()){
        case 0x12:
          selectedPid = pidVals[0];
          break;
        case 0x14:
          selectedPid = pidVals[1];
          break;
        case 0x16:
          selectedPid = pidVals[2];
          break;
        case 0x18:
          selectedPid = pidVals[3];
          break;
        case 0x22:
          selectedPid = pidVals[4];
          break;
        case 0x35:
          selectedPid = pidVals[5];
          break;
        case 0x42:
          selectedPid = pidVals[6];
          break;
        case 0x53:
          selectedPid = pidVals[7];
          break;
        case 0x63:
          selectedPid = pidVals[8];
          break;
        case 0x74:
//        disable pid
          pidEnabled = false;
          return true;
          break;
        case 0x84:
//        enable pid
          pidEnabled = true;
          break;
        case 0x92:
//          disable gyro
            gyroEnabled = false;
        case 0xA3:
//            enable gyro
            gyroEnabled = true;
        break;
        case 0xB2:
        break;
        case 0xB6:
        break;
        case 0xC1:
        break;
        case 0xC5:
        break;
        case 0xD1:
        break;
        case 0xD7:
        break;
        case 0xE9:
        break;
        case 0xF2:
        break;
        default:
//        command not found
          return false;
          break;
      }
      if (adjustManual){
      
      }
      if (adjustPid){
//      we need a value for the pid. Maybe change if other commands need floats
        byte valBytes[4];
        for (int i = 0; i < 4; i++){
          int currVal = CAN.read();
          if (currVal == -1){
  //          no more bytes, something went wrong
              return false;
          }
          valBytes[i] = (byte)currVal;
        }
        value = *((float*)valBytes);
      }
    }
  }
  if (adjustPid){
    selectedPid->totalError += (selectedPid->targetVal - value) * millis();
    selectedPid->targetVal = value;
  }
  return true;
}

void allPidLoop(){
  //check acceleartion values later
  float movements[6];
//  f, s, l, p, r, y
//  maybe limit to 20 or so for each?
  movements[0] = pidLoop(pidVals[0]->targetVal - accelData.data[0], pidVals[0]);
  movements[1] = pidLoop(pidVals[1]->targetVal - accelData.data[1], pidVals[1]);
  movements[2] = pidLoop(pidVals[2]->targetVal - accelData.data[2], pidVals[2]);
  if (gyroEnabled){
    movements[3] = pidLoop(pidVals[3]->targetVal - gyroData.data[0], pidVals[3]);
    movements[4] = pidLoop(pidVals[4]->targetVal - gyroData.data[1], pidVals[4]);
    movements[5] = pidLoop(pidVals[5]->targetVal - gyroData.data[2], pidVals[5]);
  }
  else{
    movements[3] = pidLoop(getAngleError(orientationData.data[0], pidVals[0]->targetVal), pidVals[6]);
    movements[4] = pidLoop(getAngleError(orientationData.data[1], pidVals[1]->targetVal), pidVals[7]);
    movements[5] = pidLoop(getAngleError(orientationData.data[2], pidVals[2]->targetVal), pidVals[8]);
  }
  for (int i = 0; i < 6; i++){
    if (movements[i] > 100)
      movements[i] = 100;
    if (movements[i] < -100)
      movements[i] = -100;
  }
  parseManualMoveCommand(movements[0], movements[1], movements[2], movements[3], movements[4], movements[5]);
}

float getAngleError(float currAngle, float targetAngle){
//  currAngle is from 0-359
  currAngle -= -180;
  float error = 0;
  float eP = targetAngle - currAngle;
  float eN = -1 * (360 - eP);
  if (abs(eP) > abs(eN)){
    return eP;
  }
  else{
    return eN;
  }
}

float pidLoop(float currVal, pidc_t *pidVals){
  float combined = 0;
  float error = 
//  calc proportional
  pidVals->totalError += error;
  combined += pidVals->pConstant * error;
//  calc integral
  combined += pidVals->iConstant * pidVals->totalError; 
//  calc differential
  combined += pidVals->dConstant * (error - pidVals->pastError);

  pidVals->pastError = error;
//  outputFunc(combined);
  return combined;
}


//NEED TO CHECK IF THIS WORKS WELL, I DON'T THINK IT WILL (average may screw things up)
void parseManualMoveCommand(float f, float s, float u, float p, float r, float y){
  float frontSideTotal = abs(f) + abs(s) + abs(y);
  float upTotal = abs(u) + abs(p) + abs(r);
//  thruster totals used to average movement
  int thrusterVals[8];
  thrusterVals[0] = floor(f - s - y);
  thrusterVals[1] = floor(f + s + y);
  thrusterVals[2] = floor(f - s + y);
  thrusterVals[3] = floor(f + s - y);

  thrusterVals[4] = floor(u + p - r);
  thrusterVals[5] = floor(u + p + r);
  thrusterVals[6] = floor(u - p + r);
  thrusterVals[7] = floor(u - p - r);

  for (int i = 0; i < 4; i++){
    thrusterVals[i] /= frontSideTotal;
    thrusterVals[4+i] /= upTotal;
  }
  moveAllThrusters(thrusterVals);
}

void moveAllThrusters(int* thrusterVals){
//  thrusterVals between -100 and 100
  for (int i = 0; i < 8; i++){
//    between 1000 and 2000
    thrusters[i].writeMicroseconds(thrusterVals[i] * 5 + 1500);
  }
}

void parseManualMoveCommand(int f, int s, int u, int p, int r, int y){
//  forward, side, up, pitch, roll, yaw
//arguments are between 0 and 200 (turn into -100 - 100)
//  forward -= 100;
//  side -= 100;
//  up -= 100;
//  pitch -= 100;
//  roll -= 100;
//  yaw -= 100;
//
  int frontSideTotal = abs(f) + abs(s) + abs(y);
  int upTotal = abs(u) + abs(p) + abs(r);
//  thruster totals used to average movement
  int thrusterVals[8];
  thrusterVals[0] = f - s -y;
  thrusterVals[1] = f + s + y;
  thrusterVals[2] = f - s + y;
  thrusterVals[3] = f + s - y;

  thrusterVals[4] = u + p - r;
  thrusterVals[5] = u + p + r;
  thrusterVals[6] = u - p + r;
  thrusterVals[7] = u - p - r;

  for (int i = 0; i < 4; i++){
    thrusterVals[i] /= frontSideTotal;
    thrusterVals[4+i] /= upTotal;
  }
  moveAllThrusters(thrusterVals);
}

//void parseManualMoveCommand(int *thrustVals){
//  parseManualMoveCommand(thrustVals[0], thrustVals[1], thrustVals[2], thrustVals[3], thrustVals[4]. thrustVals[5]){
//    
//    }
//}
