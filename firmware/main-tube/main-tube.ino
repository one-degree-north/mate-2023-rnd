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
#define MINTHRUST 5 // minimum thrust percentage for blades to move
#define MAXTHRUSTOVERTIME 0.001 // maximum change in thrust percentage over time permited
#define THRUSTWRITEDELAY 4
int thrustDelay = THRUSTWRITEDELAY;
int thrustDeltaTime = 0;

int thrusterPins[] = {5, 6, 9, 10, 11, 12, 4, 0};
int CAN_ID = 0x32;
Servo thrusters[8];
bool serialDebug = false;

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

int deltaTime;
unsigned long pastTime;

void setup() {
  for (int i = 0; i < 8; i++){
    thrusters[i].attach(thrusterPins[i]);
    thrusters[i].writeMicroseconds(1500);
  }
  pastTime = millis();
  CAN.begin(250000);
  CAN.onReceive(readCan);
  bno.begin();
  Serial.begin(9600);
  delay(7500);
}

void loop() {
  unsigned long now = millis();
  deltaTime = now - pastTime;
  pastTime = now;
  // control movement
//  sensorUpdateLoop();
  // if (!pidEnabled){
  //   parseManualMoveCommand(manualSpeeds[0], manualSpeeds[1], manualSpeeds[2], manualSpeeds[3], manualSpeeds[4], manualSpeeds[5]);
  // }
  // moveThrusters(tMov);
//  timer between writing PWM
  if (thrustDelay < 0){
//    Serial.print("delta time: ");
//    Serial.print(thrustDeltaTime);
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
  if (updateClock <= 0){
    updateClock = BNO_RATE;
    bno.getEvent(&orientationData, Adafruit_BNO055::VECTOR_EULER);
    bno.getEvent(&accelData, Adafruit_BNO055::VECTOR_LINEARACCEL);
    bno.getEvent(&gyroData, Adafruit_BNO055::VECTOR_GYROSCOPE);
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

          // Serial.println("sending sensor data");
          // Serial.println(i*3+j, BIN);
          // Serial.println(((byte*)&val)[0], BIN);
          // Serial.println(((byte*)&val)[1], BIN);
          // Serial.println(((byte*)&val)[2], BIN);
          // Serial.println(((byte*)&val)[3], BIN);

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

void setThrustPercent(){
  pidEnabled = false;
  for (int i = 0; i < 8; i++){
    pidVals[i]->targetVal = 0;
  }
  for (int i = 0; i < 6; i++){
    ((float*)&tMov)[i] = 0;
  }
}

void setPid(){
  pidEnabled = true;
  for (int i = 0; i < 8; i++){
    pidVals[i]->targetVal = 0;
  }
  for (int i = 0; i < 6; i++){
    ((float*)&tMov)[i] = 0;
  }
}

void readCan(int packetLength){
//  set command values all to 0
  uint16_t idPacket = CAN.packetId();
  byte device = idPacket>>8;
  byte destDevice = (idPacket<<3)>>8;
  byte command = (idPacket<<6)>>6;
  
  for (int i = 0; i < 8; i++){
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
      return;
    }
    for (int i = 0; i < packetLength; i++){
      commandValues[i] = CAN.read();
    }
//    commandPayload = ((input_t*)commandValues)[0];
    switch (command){
      case 0x01:  // set settings ()
      break;
      case 0x02:  
      break;
      case 0x0A:  // set front acceleration
        setPid();
        pidF.targetVal = ((float*)commandValues)[0];
      break;
      case 0x0B:  // set side acceleration
        setPid();
        pidS.targetVal = ((float*)commandValues)[0];
      break;
      case 0x0C:  // set up acceleration
        setPid();
        pidU.targetVal = ((float*)commandValues)[0];
      break;
      case 0x0D:  // set roll acceleration
        setPid();
        pidR.targetVal = ((float*)commandValues)[0];
      break;
      case 0x0E:  // set pitch acceleration
        setPid();
        pidP.targetVal = ((float*)commandValues)[0];
      break;
      case 0x0F:  // set yaw acceleration
        setPid();
        pidY.targetVal = ((float*)commandValues)[0];
      break;
      case 0x10:  // set front percent (manual)
        setThrustPercent();
        tMov.f = ((float*)commandValues)[0];
      break;
      case 0x11:  // set side percent (manual)
        setThrustPercent();
        tMov.s = ((float*)commandValues)[0];
      break;
      case 0x12:  // set up percent (manual)
        setThrustPercent();
        tMov.u = ((float*)commandValues)[0];
      break;
      case 0x13:  // set roll percent (manual)
        setThrustPercent();
        tMov.r = ((float*)commandValues)[0];
      break;
      case 0x14:  // set pitch percent (manual)
        setThrustPercent();
        tMov.p = ((float*)commandValues)[0];
      break;
      case 0x15:  // set yaw percent (manual)
        setThrustPercent();
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

void moveThrusters(move_t tMov){
  if (serialDebug){
    Serial.println("----- current thruster target -----");
    Serial.print("forward: "); Serial.print(tMov.f); Serial.print(" | "); Serial.print("side: "); Serial.print(tMov.s) + Serial.print(" | ");
    Serial.print("up: "); Serial.print(tMov.u); Serial.print(" | "); Serial.print("roll: "); Serial.println(tMov.r); 
    Serial.print("pitch: "); Serial.print(tMov.p); Serial.print(" | "); Serial.print(" yaw: "); Serial.println(tMov.y);
  }

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
  // adjust thrust percent so they increase to target over time
  // all increase with the slowest
  float maxDiff = 0;
  float maxDeltaThrust = thrustDeltaTime * MAXTHRUSTOVERTIME;
  Serial.print("max delta thrust: ");
  Serial.println(maxDeltaThrust);
  for (int i = 0; i < 6; i++){
    float currT = ((float*)&tMov)[i];
    float currP = ((float*)&pMov)[i];
    if (abs(currP - currT) > maxDiff){
      maxDiff = abs(currP - currT);
    }
  }
  if (maxDiff != 0){
  for (int i = 0; i < 6; i++){
    float currT = ((float*)&tMov)[i];
    float currP = ((float*)&pMov)[i];
    float maxIndDeltaT = (currT - currP) / maxDiff * maxDeltaThrust; // individual max delta
    Serial.print("max ind delta: ");
    Serial.println(maxIndDeltaT);
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
