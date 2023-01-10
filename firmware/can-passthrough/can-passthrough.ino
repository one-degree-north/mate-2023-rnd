#include <CAN.h>

// WE DON'T HAVE USB TO CAN bus YET, SO THIS IS THE BEST WE CAN (get it???) DO FOR NOW

// #define Serial Serail1
#define HEADER 0xA0
#define FOOTER 0x0B

// data needed for writing
uint8_t command;
uint8_t data[8];
int dataLen = 0;
int currDataIndex = 0;
bool headerFound = false;

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
        case 0x0A
        break;
      }
      // currently all command just use a float, so not going to bother right now.
      dataLen = 4;
      currDataIndex++;
    }
    // read the data

    int sel = Serial.read();
    float values[3];
    for (int i = 0; i < 3; i++){
        while (!Serial.available());
        values[i] = Serial.parseFloat();
        Serial.print("value: ")
        Serial.println(values[i])
    }
    uint16_t com = 0x00;
    switch(sel){
      case '1': // set x target acceleration
        com = 0x0A;
        Serial.println("Setting f target accel");
      break;
      case '2': // set y target acceleration
        com = 0x0B;
        Serial.println("Setting s target accel");
      break;
      case '3': // set z target acceleration
        com = 0x0C;
        Serial.println("Setting u target accel");
      break;
      case '4':
        com = 0x0D;
        Serail.println("Setting ")
      break;
      case '5':
        com = 0x0F;

    }
    CAN.beginPacket(0b11000000000 + 0 + com);
    byte* floatSend = (byte*)&value;
    CAN.write(floatSend[0]);
    CAN.write(floatSend[1]);
    CAN.write(floatSend[2]);
    CAN.write(floatSend[3]);
    Serial.print("strength: ");
    Serial.println(value);
    Serial.println("sent can");
  }
}

void readCan(int canLen){
  uint16_t idPacket = CAN.packetId();
  for (int i = 0; i < canLen; i++){
    Serial.write(CAN.read());
  }
}