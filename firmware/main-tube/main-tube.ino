#include <Servo.h>
#include <CAN.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <math.h>

#define SELFID 0x23
#define BNO_RATE 10 //refresh rate, ms
#define SENSOR_RATE 100  // send rate, in 10s of ms
#define DEVICE_ID 1 //device id for use in canbus
#define MAXTHRUST 70  // maximum thrust percentage permited
#define MAXTHRUSTOVERTIME 1 // maximum change in thrust percentage over time permited 

int thrusterPins[] = {5, 6, 9, 10, 11, 12, 13, 0};
int CAN_ID = 0x32;
Servo thrusters[8];

typedef struct canInput{
  byte id;
  union{
    float fval;
    
  }u;
} input_t;

// increasing thruster speed over time (instead of changing PWM instantly)


typedef struct Movement{
  float f;
  float s;
  float u;
  float r;
  float p;
  float y;
} move_t;

move_t tMov = {0, 0, 0, 0, 0, 0}; // target move, percentage thruster strength
move_t pMov = {0, 0, 0, 0, 0, 0}; // past move, percentage thruster strength

typedef struct PID{
  float pConstant;
  float iConstant;
  float dConstant;
  float targetVal;
  float totalError;
  float pastError;
  float pastValue;
} pidc_t;

byte commandValues[8];

//BNO DATA
sensors_event_t orientationData;
sensors_event_t gyroData;
sensors_event_t accelData;

// updating PID and sending data
int imuUpdateDelay = SENSOR_RATE; // Sending BNO data rate (in 10s of ms)
int updateClock = BNO_RATE; // BNO update rate (10 ms, changing this changes imuUpdateDelay)

//manual config
int manualSpeeds[6];

//pid stuff
bool pidEnabled = true;
bool gyroEnabled = false;
pidc_t pidF = {2.2, 3.4, 2.3, 0.1, 0, 0, 0};  // forward
pidc_t pidS = {2.2, 3.4, 2.3, 0, 0, 0, 0};  // side
pidc_t pidU = {2.2, 3.4, 2.3, 0, 0, 0, 0};  // up
//pid using degree
pidc_t pidR = {2.2, 3.4, 2.3, 0, 0, 0, 0};  // roll
pidc_t pidP = {2.2, 3.4, 2.3, 0, 0, 0, 0};  // pitch
pidc_t pidY = {2.2, 3.4, 2.3, 0, 0, 0, 0};  // yaw
//pid using gyroscope
pidc_t pidRG = {2.2, 3.4, 2.3, 0, 0, 0, 0};
pidc_t pidPG = {2.2, 3.4, 2.3, 0, 0, 0, 0};
pidc_t pidYG = {2.2, 3.4, 2.3, 0, 0, 0, 0};

pidc_t* pidVals[] = {&pidF, &pidS, &pidU, &pidRG, &pidPG, &pidYG, &pidR, &pidP, &pidY};

Adafruit_BNO055 bno = Adafruit_BNO055(55);

int deltaTime;
unsigned long pastTime;

void setup() {
  for (int i = 0; i < 8; i++){
    thrusters[i].attach(thrusterPins[i]);
  }
  pastTime = millis();
  CAN.begin(500000);
  CAN.onReceive(readCan);
  bno.begin();
  Serial.begin(9600);
}

void loop() {
  unsigned long now = millis();
  deltaTime = now - pastTime;
  pastTime = now;
  // control movement
  sensorUpdateLoop();
  // if (!pidEnabled){
  //   parseManualMoveCommand(manualSpeeds[0], manualSpeeds[1], manualSpeeds[2], manualSpeeds[3], manualSpeeds[4], manualSpeeds[5]);
  // }
  // moveThrusters(tMov);
  moveThrust();
}

//updates sensor values, updates pid, and sends sensor data
void sensorUpdateLoop(){
  updateClock -= deltaTime;
  if (updateClock <= 0){
    updateClock = BNO_RATE;
    updateSensorReadings();
    if (pidEnabled){
      allPidLoop();
    }
    sendSensorData();
  }
}

void sendSensorData(){
  imuUpdateDelay--;
  if(imuUpdateDelay <= 0){
      imuUpdateDelay = SENSOR_RATE;
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

          Serial.println("sending sensor data");
          Serial.println(i*3+j, BIN);
          Serial.println(((byte*)&val)[0], BIN);
          Serial.println(((byte*)&val)[1], BIN);
          Serial.println(((byte*)&val)[2], BIN);
          Serial.println(((byte*)&val)[3], BIN);

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

void updateSensorReadings(){
  bno.getEvent(&orientationData, Adafruit_BNO055::VECTOR_EULER);
  bno.getEvent(&accelData, Adafruit_BNO055::VECTOR_LINEARACCEL);
  bno.getEvent(&gyroData, Adafruit_BNO055::VECTOR_GYROSCOPE);
}

void readCan(int packetLength){
//  set command values all to 0
  uint16_t idPacket = CAN.packetId();
  byte device = idPacket>>9;
  byte destDevice = (idPacket<<2)>>9;
  byte command = (idPacket<<4)>>4;
  
  for (int i = 0; i < 8; i++){
    commandValues[i] = 0;
  }
//  input_t commandPayload;
//  if (packetLength != 0){
//    device = commandValues[0] >> 7;
//    command = (commandValues[0] << 1) >> 7;
//00: main tube
//01: claw 1
//10: claw 2
//11: main board
    if (destDevice != 0b00){
      return;
    }
    for (int i = 0; i < packetLength; i++){
      commandValues[i] = CAN.read();
    }
//    commandPayload = ((input_t*)commandValues)[0];
    switch (command){
      case 0x09:  // set settings
      break;
      case 0x0A:  // set x acceleration
        pidF.targetVal = ((float*)commandValues)[0];
      break;
      case 0x0B:  // set y acceleration
        pidS.targetVal = ((float*)commandValues)[0];
      break;
      case 0x0C:  // set z acceleration
        pidU.targetVal = ((float*)commandValues)[0];
      break;
    }
//  }
  return;
}

void allPidLoop(){
  //check acceleartion values later
  // float movements[6];
//  f, s, l, p, r, y
//  maybe limit to 20 or so for each?
  tMov.f = pidLoop(pidVals[0]->targetVal - accelData.data[0], pidVals[0]);  // f
  tMov.s = pidLoop(pidVals[1]->targetVal - accelData.data[1], pidVals[1]);  // s
  tMov.u = pidLoop(pidVals[2]->targetVal - accelData.data[2], pidVals[2]);  // u
  if (gyroEnabled){
    tMov.p = pidLoop(pidVals[3]->targetVal - gyroData.data[0], pidVals[3]); // p
    tMov.r = pidLoop(pidVals[4]->targetVal - gyroData.data[1], pidVals[4]); // r
    tMov.y = pidLoop(pidVals[5]->targetVal - gyroData.data[2], pidVals[5]); // y
  }
  else{
    tMov.p = pidLoop(getAngleError(orientationData.data[0], pidVals[0]->targetVal), pidVals[6]);
    tMov.r = pidLoop(getAngleError(orientationData.data[1], pidVals[1]->targetVal), pidVals[7]);
    tMov.y = pidLoop(getAngleError(orientationData.data[2], pidVals[2]->targetVal), pidVals[8]);
  }
  // parseManualMoveCommand(movements[0], movements[1], movements[2], movements[3], movements[4], movements[5]);
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

float pidLoop(float error, pidc_t *pidVals){
  float combined = 0;
//  pidVals->pastError = (pidVals->targetVal - currVal);
//  pidVals->pastValue = currVal;
//  float error = pidVals->targetVal - pidVals->pastValue;
  pidVals->totalError += error*(float)(BNO_RATE)/1000.0;
//  calc proportional
  combined += pidVals->pConstant * error;
//  calc integral
  combined += pidVals->iConstant * pidVals->totalError; 
//  calc differential
  combined += pidVals->dConstant * (error - pidVals->pastError);

  pidVals->pastError = error;
//  Serial.println(combined);
  return combined;
}

void printPid(pidc_t){
  
}

//NEED TO CHECK IF THIS WORKS WELL, I DON'T THINK IT WILL (average may screw things up)
void parseManualMoveCommand(float f, float s, float u, float p, float r, float y){
  float frontSideTotal = abs(f) + abs(s) + abs(y);
  float upTotal = abs(u) + abs(p) + abs(r);
//  thruster totals used to average movement
  int thrusterVals[8];
  thrusterVals[0] = (int)floor(f - s - y);
  thrusterVals[1] = (int)floor(f + s + y);
  thrusterVals[2] = (int)floor(f - s + y);
  thrusterVals[3] = (int)floor(f + s - y);

  thrusterVals[4] = (int)floor(u + p - r);
  thrusterVals[5] = (int)floor(u + p + r);
  thrusterVals[6] = (int)floor(u - p + r);
  thrusterVals[7] = (int)floor(u - p - r);
  int maxVal = 0;
  for (int i = 0; i < 8; i++){
    int currVal = abs(thrusterVals[i]);
    if (currVal > maxVal){
      maxVal = currVal;
    }
  }
  // adjusting for ratio when over 100, todo
  if (maxVal > 100){
    for (int i = 0; i < 8; i++){
      thrusterVals[i] = (int)floor((float)thrusterVals[i]/maxVal)*100;
    }
  }
  moveAllThrusters(thrusterVals);
}

void moveAllThrusters(int* thrusterVals){
//  thrusterVals between -100 and 100
  for (int i = 0; i < 8; i++){
    Serial.print(i);
    Serial.print(": ");
    Serial.print(thrusterVals[i]);
    Serial.print(" ");
    Serial.println((int)(1500.0 + 5.0*(float)thrusterVals[i]));
    thrusters[i].writeMicroseconds((int)(1500.0 + 5.0*(float)thrusterVals[i]));
  }
}

void parseManualMoveCommand(int f, int s, int u, int p, int r, int y){
  Serial.println("WTFFFF");
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
    Serial.println(frontSideTotal);
    Serial.println(thrusterVals[i]);
    thrusterVals[i] /= frontSideTotal;
    Serial.println(thrusterVals[i]);
    Serial.println("---");
    thrusterVals[4+i] /= upTotal;
  }
  moveAllThrusters(thrusterVals);
}

void moveThrusters(move_t tMov){
  float thrusterVals[8];
  thrusterVals[0] = tMov.f - tMov.s - tMov.y;
  thrusterVals[1] = tMov.f + tMov.s + tMov.y;
  thrusterVals[2] = tMov.f - tMov.s + tMov.y;
  thrusterVals[3] = tMov.f + tMov.s - tMov.y;

  thrusterVals[4] = tMov.u + tMov.p - tMov.r;
  thrusterVals[5] = tMov.u + tMov.p + tMov.r;
  thrusterVals[6] = tMov.u - tMov.p + tMov.r;
  thrusterVals[7] = tMov.u - tMov.p - tMov.r;
  // if any thruster vals are greater than MAXTHRUST (PWM), scale everything so that it's fine
  // I'm not sure if scaling everything linearly is actually correct (scaling tMov values seems to be the correct choice, but eh.)
  float thrustPercent = 1;
  for (int i = 0; i < 8; i++){
    if (thrusterVals[i] != 0){
      float currThrustPercent = abs(MAXTHRUST/thrusterVals[i]);
      if (currThrustPercent < thrustPercent){
        thrustPercent = currThrustPercent;
      }
    }
  }
  for (int i = 0; i < 8; i++){
    thrusters[i].writeMicroseconds(1500 + (int)(thrusterVals[i]*thrustPercent*5.0));
  }
}

void moveThrust(){
  // all increase with the slowest
  float maxDiff = 0;
  float maxDeltaThrust = deltaTime * MAXTHRUSTOVERTIME;
  for (int i = 0; i < 8; i++){
    float currT = ((float*)&tMov)[i];
    float currP = ((float*)&pMov)[i];
    if (abs(currP - currT) > maxDiff){
      maxDiff = abs(currP - currT);
    }
  }
  for (int i = 0; i < 8; i++){
    float currT = ((float*)&tMov)[i];
    float currP = ((float*)&pMov)[i];
    float maxIndDeltaT = (currT - currP) / maxDiff * MAXTHRUSTOVERTIME;
    if (currT > currP){
      if (currT > currP + maxIndDeltaT){
        ((float*)&pMov)[i] += maxIndDeltaT;
      }
      else{
        ((float*)&pMov)[i] = currT;
      }
    }
    else if (currT < currP){
      if (currT < currP - maxIndDeltaT){
        ((float*)&pMov)[i] += maxIndDeltaT;
      }
      else{
        ((float*)&pMov)[i] = currT;
      }
    }
  }
  moveThrusters(pMov);
  // all increase independently
  // for (int i = 0; i < 8; i++){
  //   float currT = ((float*)&tMov)[i];
  //   float currP = ((float*)&pMov)[i];
  //   float maxDiff = deltaTime * MAXTHRUSTOVERTIME;
  //   if (currT > currP){
  //     if (currT > currP + maxDiff){
  //       ((float*)&pMov)[i] += maxDiff;
  //     }
  //     else{
  //       ((float*)&pMov)[i] = currT;
  //     }
  //   }
  //   else if (currT < currP){
  //     if (currT < currP - maxDiff){
  //       ((float*)&pMov)[i] -= maxDiff;
  //     }
  //     else{
  //       ((float*)&pMov)[i] = currT;
  //     }
  //   }
  // }
}