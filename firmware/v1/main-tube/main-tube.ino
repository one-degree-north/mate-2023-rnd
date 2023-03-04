#include <Servo.h>
#include <CAN.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <math.h>

#define SELFID 0x23
#define BNO_RATE 25 //refresh rate, ms
#define SENSOR_RATE 4  // send rate, in BNO_RATE ms
#define DEVICE_ID 1 //device id for use in canbus
#define MAXTHRUST 30  // maximum thrust percentage permited
#define MINTHRUST 5 // minimum thrust percentage for blades to move
#define MAXTHRUSTOVERTIME 1 // maximum change in thrust percentage over time permited
#define THRUSTWRITEDELAY 4

#define DEBUG_SERIAL Serial

// thrusters
long thrustDelay = THRUSTWRITEDELAY;
long thrustDeltaTime = 0;
bool reverseThrusts[] = {false, true, false, false, false, true, true, false};
int thrusterPins[] = {25, 11, 10, 24, 19, 12, 9, 23};
/*
Thruster pin configuration
0: right forward, 7, backward at 1200
1: left forward, 2, forward at 1200
2: left down, 0, backward at 1200
3: right down, 6, backward at 1200
upward facing
4: right forward, 5, down at 1200
5: left forward, 3, up at 1200
6: left down, 1, up at 1200
7: right down, 4, down at 1200
*/
int CAN_ID = 0x32;
Servo thrusters[8];
int camServoPins[] = {4};
Servo camServo[1];

// settings
bool serialDebug = true;
bool sendPidError = true;
int pastThrustVals[] = {1492, 1492, 1492, 1492, 1492, 1492, 1492, 1492};

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
} pidc_t;

byte commandValues[256];

//BNO DATA
sensors_event_t orientationData;
sensors_event_t gyroData;
sensors_event_t accelData;

// updating PID and sending data
long imuUpdateDelay = SENSOR_RATE; // Sending BNO data rate (in 10s of ms)
long updateClock = BNO_RATE; // BNO update rate (10 ms, changing this changes imuUpdateDelay)

//manual config
int manualSpeeds[6];

//pid stuff
bool pidEnabled = false;
bool gyroEnabled = false;
pidc_t pidF = {2.2, 3.4, 2.3, 0, 0, 0};  // forward
pidc_t pidS = {2.2, 3.4, 2.3, 0, 0, 0};  // side
pidc_t pidU = {2.2, 3.4, 2.3, 0, 0, 0};  // up
//pid using degree
pidc_t pidR = {2.2, 3.4, 2.3, 0, 0, 0};  // roll
pidc_t pidP = {2.2, 3.4, 2.3, 0, 0, 0};  // pitch
pidc_t pidY = {2.2, 3.4, 2.3, 0, 0, 0};  // yaw
//pid using gyroscope
pidc_t pidRG = {2.2, 3.4, 2.3, 0, 0, 0};
pidc_t pidPG = {2.2, 3.4, 2.3, 0, 0, 0};
pidc_t pidYG = {2.2, 3.4, 2.3, 0, 0, 0};

pidc_t* pidVals[] = {&pidF, &pidS, &pidU, &pidRG, &pidPG, &pidYG, &pidR, &pidP, &pidY};

Adafruit_BNO055 bno = Adafruit_BNO055(55);

unsigned long deltaTime;
unsigned long pastTime;

void setup() {
  for (int i = 0; i < 8; i++){
    thrusters[i].attach(thrusterPins[i]);
//    thrusters[i].writeMicroseconds(1500);
  }
 for (int i = 0; i < 1; i++){
   camServo[i].attach(camServoPins[i]);
   camServo[i].write(0);
 }
  pastTime = millis();
  CAN.begin(500000);
  CAN.onReceive(readCan);
  bno.begin();
  Serial.begin(9600);
  // initialize thrusters
  for (int i = 0; i < 8; i++){
    thrusters[i].writeMicroseconds(2000);
  }
  delay(4);
  for (int i = 0; i < 8; i++){
    thrusters[i].writeMicroseconds(1500);
  }
  delay(7500);
}

void loop() {
  unsigned long now = millis();
  deltaTime = now - pastTime;
  pastTime = now;
  // control movement
   sensorUpdateLoop();
//  timer between writing PWM
  if (thrustDelay < 0){
//    Serial.print("delta time: ");
//    Serial.println(thrustDeltaTime);
    moveThrust();
    thrustDeltaTime = 0;
    thrustDelay = THRUSTWRITEDELAY;
  }
  else{
    thrustDeltaTime += deltaTime;
    thrustDelay -= deltaTime;
  }
}

//updates sensor values, updates pid, and sends sensor data
void sensorUpdateLoop(){
  updateClock -= deltaTime;
  //Serial.print("updateClock: ");
  //Serial.println(updateClock);
  if (updateClock <= 0){
    updateClock = BNO_RATE;
    //delayMicroseconds(1000);
    bno.getEvent(&orientationData, Adafruit_BNO055::VECTOR_EULER);
    //delayMicroseconds(1000);
    bno.getEvent(&accelData, Adafruit_BNO055::VECTOR_LINEARACCEL);
    //delayMicroseconds(1000);
    bno.getEvent(&gyroData, Adafruit_BNO055::VECTOR_GYROSCOPE);
    //delayMicroseconds(1000);
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
              val = gyroData.data[j];
            break;
            case 2:
              val = accelData.data[j];
            break;
          }
          CAN.beginPacket(0b00001100000 + ((byte(i))<<2) + j);
          CAN.write(((byte*)&val)[0]);
          CAN.write(((byte*)&val)[1]);
          CAN.write(((byte*)&val)[2]);
          CAN.write(((byte*)&val)[3]);
          CAN.endPacket();
        }
    }
//    send pid error
    if (pidEnabled && serialDebug){
    for (int i = 0; i < 3; i++){
      float error = pidVals[i]->pastError;
      CAN.beginPacket(0b00001100000 + (byte(0x05)<<2) + i);
      CAN.write(((byte*)&error)[0]);
          CAN.write(((byte*)&error)[1]);
          CAN.write(((byte*)&error)[2]);
          CAN.write(((byte*)&error)[3]);
      CAN.endPacket();
    }
    for (int i = 3; i < 6; i++){
      float error = pidVals[i+3]->pastError;
      CAN.beginPacket(0b00001100000 + (byte(0x06)<<2) + i);
      CAN.write(((byte*)&error)[0]);
          CAN.write(((byte*)&error)[1]);
          CAN.write(((byte*)&error)[2]);
          CAN.write(((byte*)&error)[3]);
      CAN.endPacket();
    }
    }
  }
}

void setThrustPercent(){
  pidEnabled = false;
}

void setPid(){
  pidEnabled = true;
}

void readCan(int packetLength){
//  set command values all to 0
  long idPacket = CAN.packetId();
  byte device = idPacket>>8;
  byte destDevice = (idPacket&0b00011100000)>>5;
  byte command = (idPacket&0b00000011111);
  if (serialDebug){
    Serial.println("--recieved data--")
    Serial.print("id: ");
    Serial.println(idPacket, HEX);
    Serial.print("send device: ");
    Serial.println(device, HEX);
    Serial.print("destination device: ")
    Serial.println(destDevice, HEX);
    Serial.print("command: ");
    Serial.println(command, HEX);
    Serial.print("packet len: ");
    Serial.println(packetLength);
  }
  for (int i = 0; i < 256; i++){
    commandValues[i] = 0;
  }
//  input_t commandPayload;
//  if (packetLength != 0){
//    device = commandValues[0] >> 7;
//    command = (commandValues[0] << 1) >> 7;
//000: main tube
//001: claw 1
//010: claw 2
//011: main board
    if (destDevice != 0b000){
      // message was not sent for main-tube!
      return;
    }
    for (int i = 0; i < packetLength; i++){
      commandValues[i] = CAN.read();
    }
    switch (command){
      case 0x01:  // set settings ()
        if (packetLength == 1){
          pidEnabled = 0
        }
      break;
     case 0x05:  // camera
//        Serial.print("moving cam");
//        Serial.println("degree");
//        Serial.println(commandValues[4]);
//        Serial.println(((int*)commandValues)[0]);
       moveCamServo(((int*)commandValues)[0], commandValues[4]);
     break;
      case 0x02:  // change pid front
        if (packetLength == 6){
          byte chosenPidNum = commandValues[0];
          byte sel = commandValues[1];
          float pidValue = ((float*)(&(commandValues[2])))[0];
          if (serialDebug){
            Serial.print("----change pid command----");
            Serial.print("chosenPid: ");
            Serial.println(chosenPidNum);
            Serial.print("pidSelect: ");
            Serial.println(sel);
            Serial.println("new val: ");
            Serial.print(pidValue);
          }
          if (chosenPidNum < 6){
            pidc_t* chosenPid = pidVals[chosenPidNum];
            if (sel < 3){
              ((float*)chosenPid)[sel] = pidValue;
            }
            if (serialDebug){
              Serial.print("pid p: ");
              Serial.println(chosenPid->pConstant);
              Serial.print("pid i: ");
              Serial.println(chosenPid->iConstant);
              Serial.print("pid d: ");
              Serial.println(chosenPid->dConstant);
            }
          }
        }
      break;
      case 0x0A:  // set front acceleration
        setPid();
        if (serialDebug){
          Serial.print("PID front: ");
          Serial.println(((float*)commandValues)[0]);
        }
        pidF.targetVal = ((float*)commandValues)[0];
      break;
      case 0x0B:  // set side acceleration
        setPid();
        if (serialDebug){
          Serial.print("PID side: ");
          Serial.println(((float*)commandValues)[0]);
        }
        pidS.targetVal = ((float*)commandValues)[0];
      break;
      case 0x0C:  // set up acceleration
        setPid();
        if (serialDebug){
          Serial.print("PID up: ");
          Serial.println(((float*)commandValues)[0]);
        }
        pidU.targetVal = ((float*)commandValues)[0];
      break;
      case 0x0D:  // set roll acceleration
        setPid();
        if (serialDebug){
          Serial.print("PID roll: ");
          Serial.println(((float*)commandValues)[0]);
        }
        pidR.targetVal = ((float*)commandValues)[0];
      break;
      case 0x0E:  // set pitch acceleration
        setPid();
        if (serialDebug){
          Serial.print("PID pitch: ");
          Serial.println(((float*)commandValues)[0]);
        }
        pidP.targetVal = ((float*)commandValues)[0];
      break;
      case 0x0F:  // set yaw acceleration
        setPid();
        if (serialDebug){
          Serial.print("PID yaw: ");
          Serial.println(((float*)commandValues)[0]);
        }
        pidY.targetVal = ((float*)commandValues)[0];
      break;
      case 0x10:  // set front percent (manual)
        setThrustPercent();
        if (serialDebug){
          Serial.print("front: ");
          Serial.println(((float*)commandValues)[0]);
        }
        tMov.f = ((float*)commandValues)[0];
//        Serial.print("A");
//        Serial.print(tMov.f);
      break;
      case 0x11:  // set side percent (manual)
        setThrustPercent();
        if (serialDebug){
          Serial.print("side: ");
          Serial.println(((float*)commandValues)[0]);
        }
        tMov.s = ((float*)commandValues)[0];
      break;
      case 0x12:  // set up percent (manual)
        setThrustPercent();
        if (serialDebug){
          Serial.print("up: ");
          Serial.println(((float*)commandValues)[0]);
        }
        tMov.u = ((float*)commandValues)[0];
      break;
      case 0x13:  // set roll percent (manual)
        setThrustPercent();
        if (serialDebug){
          Serial.print("roll: ");
          Serial.println(((float*)commandValues)[0]);
        }
        tMov.r = ((float*)commandValues)[0];
      break;
      case 0x14:  // set pitch percent (manual)
        setThrustPercent();
        if (serialDebug){
          Serial.print("pitch: ");
          Serial.println(((float*)commandValues)[0]);
        }
        tMov.p = ((float*)commandValues)[0];
      break;
      case 0x15:  // set yaw percent (manual)
        setThrustPercent();
        if (serialDebug){
          Serial.print("yaw: ");
          Serial.println(((float*)commandValues)[0]);
        }
        tMov.y = ((float*)commandValues)[0];
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
//  currAngle is from 0-359, targetAngle also from 0-359
  float error = targetAngle - currAngle;
  error = (error + 180)%360-180;
  return error;
}

float pidLoop(float error, pidc_t *pidVals){
  float combined = 0;
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

void printPid(pidc_t pidVal, float error, float currValue){
  Serial.println("x - orientation");
  Serial.print("target: "); Serial.print(pidVal.targetVal); Serial.print(" | "); Serial.print("current: "); Serial.print(currValue); Serial.print(" | ");
  Serial.print(" error: "); Serial.print(error); Serial.print(" | "); Serial.print("total error: "); Serial.println(pidVal.totalError);
}

void moveThrusters(move_t mov){ // move thrusters given move_t
  if (serialDebug){
//    Serial.println("----- current thruster target -----");
//    Serial.print("forward: "); Serial.print(mov.f); Serial.print(" | "); Serial.print("side: "); Serial.print(mov.s) + Serial.print(" | ");
//    Serial.print("up: "); Serial.print(mov.u); Serial.print(" | "); Serial.print("roll: "); Serial.println(mov.r); 
//    Serial.print("pitch: "); Serial.print(mov.p); Serial.print(" | "); Serial.print(" yaw: "); Serial.println(mov.y);
  }
  
  float thrusterVals[8];
  thrusterVals[0] = mov.f - mov.s - mov.y;
  thrusterVals[1] = mov.f + mov.s + mov.y;
  thrusterVals[2] = mov.f - mov.s + mov.y;
  thrusterVals[3] = mov.f + mov.s - mov.y;

  thrusterVals[4] = mov.u + mov.p - mov.r;
  thrusterVals[5] = mov.u + mov.p + mov.r;
  thrusterVals[6] = mov.u - mov.p + mov.r;
  thrusterVals[7] = mov.u - mov.p - mov.r;
  // if any thruster vals are greater than MAXTHRUST (PWM), scale everything down
  // I'm not sure if scaling everything linearly is actually correct
  float thrustPercent = 1;
  for (int i = 0; i < 8; i++){
    if (thrusterVals[i] != 0){
      float currThrustPercent = abs(MAXTHRUST/thrusterVals[i]);
      if (currThrustPercent < thrustPercent){
        thrustPercent = currThrustPercent;
      }
    }
  }
//  Serial.println("----- current thruster target -----");
//      Serial.print("forward: "); Serial.print(mov.f); Serial.print(" | "); Serial.print("side: "); Serial.print(mov.s) + Serial.print(" | ");
//      Serial.print("up: "); Serial.print(mov.u); Serial.print(" | "); Serial.print("roll: "); Serial.println(mov.r); 
//      Serial.print("pitch: "); Serial.print(mov.p); Serial.print(" | "); Serial.print(" yaw: "); Serial.println(mov.y);
  for (int i = 0; i < 8; i++){
    int thrust;
    if (reverseThrusts[i]){
      thrust = 1492 - (int)(thrusterVals[i]*thrustPercent*5.0);
    }
    else{
       thrust = 1492 + (int)(thrusterVals[i]*thrustPercent*5.0);
    }
    if (pastThrustVals[i] != thrust){
//      Serial.print("thruster: ");
//      Serial.print(i);
//      Serial.print(" ");
//      Serial.println(thrust);
      thrusters[i].writeMicroseconds(thrust);
      pastThrustVals[i] = thrust;
    }
  }
}

void moveThrust(){  // adjust so that thrusters increase slowly over time
  // adjust thrust percent so they increase to target over time
  // all increase with the slowest
  float maxDiff = 0;
  float maxDeltaThrust = thrustDeltaTime * MAXTHRUSTOVERTIME;
  for (int i = 0; i < 6; i++){
    float currT = ((float*)&tMov)[i];
    float currP = ((float*)&pMov)[i];
    if (abs(currP - currT) > maxDiff){
      maxDiff = abs(currP - currT);
    }
  }
//  Serial.println(maxDiff);
  if (maxDiff != 0){
    for (int i = 0; i < 6; i++){
      float currT = ((float*)&tMov)[i];
      float currP = ((float*)&pMov)[i];
      float maxIndDeltaT = (currT - currP) / maxDiff * maxDeltaThrust; // individual max delta

      if (i == 0){
//        Serial.println(maxIndDeltaT);
      }
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
  //    adjusting for mininum thrust allowed
      if (-MINTHRUST < currP && currP < MINTHRUST) {
         // thrust is within "snap" range
         if (currT > MINTHRUST) {
            ((float*)&pMov)[i] = MINTHRUST;
         } 
         else if (currT < -MINTHRUST) {
            ((float*)&pMov)[i] = -MINTHRUST;
         } else {
            ((float*)&pMov)[i] = 0;
         }
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

void moveCamServo(int degree, byte pin){
//  Serial.println("degree");
//  Serial.println(degree);
//  Serial.println(int(pin));
 camServo[int(pin)].write(degree);
}
