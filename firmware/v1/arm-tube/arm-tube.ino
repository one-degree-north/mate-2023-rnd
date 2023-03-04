#include <CAN.h>
#define BNO_RATE 25 //refresh rate, ms
#define DEVICE_ID 1 //device id for use in canbus
#define FLASHLIGHT_PIN 4

Servo clawServos[2];
int servoPins[] = {12, 11};
byte commandValues[256];
bool serialDebug = true;

void setup() {
  pinMode(FLASHLIGHT_PIN, OUTPUT);
 for (int i = 0; i < 1; i++){
   clawServos[i].attach(camServoPins[i]);
//    clawServos[i].write(0);
 }
  pastTime = millis();
  CAN.begin(500000);
  CAN.onReceive(readCan);
//  if (serialDebug){
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
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
    if (destDevice != DEVICE_ID){
      // message was not sent for main-tube!
      return;
    }
    for (int i = 0; i < packetLength; i++){
      commandValues[i] = CAN.read();
    }
    switch (command){
      case 0x01:  // set settings ()
        if (packetLength == 1){
        //   pidEnabled = 0
        }
      break;
     case 0x05:  // arm servo
        if (packetLength == 5){
            writeServos(((int*)commandValues)[0], commandValues[4]);
        }
        break;
    case 0x06:
    if (packetLength == 1){
        if (commandValues[0] == 0){ // turn flashlight off
            digitalWrite(FLASHLIGHT_PIN, LOW);
        }
        else{   // turn flashlight on
            digitalWrite(FLASHLIGHT_PIN, HIGH);
        }
    }
    }
//  }
  return;
}

void writeServos(byte servo, int degree){
    if (servo < 2){
        clawServos[servo].write(degree);
    }
}