#include <CAN.h>

// WE DON'T HAVE USB TO CAN bus YET, SO THIS IS THE BEST WE CAN (get it???) DO FOR NOW

// #define Serial Serail1
#define HEADER 0xA0
#define FOOTER 0x0B

// data needed for writing
uint8_t command;
uint8_t data[20];
int dataLen = 0;
int currDataIndex = 0;
bool headerFound = false;
byte deviceSel = 0x00;

void setup() {
  // put your setup code here, to run once:
  CAN.begin(250000);
  Serial.begin(9600);
  CAN.onReceive(readCan);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available()){
    uint8_t val = Serial.read();
    // check for header
    if (!headerFound){
      if (val == HEADER){
        headerFound = true;
        currDataIndex++;
      }
    }
    // get the command byte and expected length of data
    else if (currDataIndex == 0){
      command = val;
      // get length of data to read
      switch (command){
        case 0x1A:
          dataLen = 12;
          deviceSel = 0x00;
        break;
        case 0x1B:
          dataLen = 12;
          deviceSel = 0x00;
        break;
        default:
          resetWriteData();
        break;
      }
      currDataIndex++;
    }
    // read the data
    else if (currDataIndex <= expectedDataLength){
      data[currDataIndex-1] = val;
      currDataIndex++;
    }
    else{ // check footer
      if (val == FOOTER){
        // send data!
        switch (command){
          case 0x1A:
            for (int i = 0; i < 6; i++){
              CAN.beginPacket(0b011000000000 + deviceSel<<8 + command);
              for (int j = 0; j < dataLen; j++){
                CAN.write(data[i]);
              }
              CAN.endPacket();
            }
          break;
          case 0x1B:
            for (int i = 0; i < 6; i++){
              CAN.beginPacket(0b011000000000 + deviceSel<<8 + command);
              for (int j = 0; j < dataLen; j++){
                CAN.write(data[i]);
              }
              CAN.endPacket();
            }
          break;
        }
      }
      resetWriteData();
    }
    // int sel = Serial.read();
    // float values[3];
    // for (int i = 0; i < 3; i++){
    //     while (!Serial.available());
    //     values[i] = Serial.parseFloat();
    //     Serial.print("value: ")
    //     Serial.println(values[i])
    // }
    // uint16_t deviceSel = 0x00;
    // switch(sel){
    //   case '1': // set x target acceleration
    //     deviceSel = 0x0A;
    //     // Serial.println("Setting f target accel");
    //   break;
    //   case '2': // set y target acceleration
    //     deviceSel = 0x0B;
    //     // Serial.println("Setting s target accel");
    //   break;
    //   case '3': // set z target acceleration
    //     deviceSel = 0x0C;
    //     // Serial.println("Setting u target accel");
    //   break;
    //   case '4':
    //     deviceSel = 0x0D;
    //     // Serail.println("Setting ")
    //   break;
    //   case '5':
    //     deviceSel = 0x0F;
    // }
    // CAN.beginPacket(0b11000000000 + 0 + deviceSel);
    // byte* floatSend = (byte*)&value;
    // CAN.write(floatSend[0]);
    // CAN.write(floatSend[1]);
    // CAN.write(floatSend[2]);
    // CAN.write(floatSend[3]);
    // Serial.print("strength: ");
    // Serial.println(value);
    // Serial.println("sent can");
  }
}

void resetWriteData(){
  currDataIndex = 0;
  for (int i = 0; i < 20; i++){
    data[i] = 0;
  }
  headerFound = false;
  dataLen = 0;
}

void readCan(int canLen){
  uint16_t idPacket = CAN.packetId();
  uint16_t readDevice = (idPacket & 0b00011100000) >> 5;
  uint16_t readCommand = idPacket & 0b00000011111;
  if (readDevice == 0b011){
    Serial.write(HEADER);
    Serial.write(readCommand);
    for (int i = 0; i < canLen; i++){
      Serial.write(CAN.read());
    }
    Serial.write(FOOTER);
  }
}