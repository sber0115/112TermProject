#include <AFMotor.h>
#include <string.h>

AF_DCMotor m1(1); //motor on lower left
AF_DCMotor m2(2); //motor on lower right
AF_DCMotor m3(3); //motor on upper right
AF_DCMotor m4(4); //motor on upper left

const byte numChars = 32;
char receivedChars[numChars];

boolean newData = false;

//a 90 degree rotation entails a delay of 280 --> when passing in parameters for the move
//motors function calculate some ratio in the python code such that a turn is executed with the delay


void setup() {
    Serial.begin(9600);
    Serial.println("<Arduino is ready>");
}

void loop() {
    recvWithStartEndMarkers();
    showNewData();
  
    
}

void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;

    
 
    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
                
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}




void moveMotors(){
  Serial.print("moving the motors");

  const byte totalNum = 3;
  
  char delayArray[totalNum];
  int delayIndex = 0;

  
  
  for (int index = 2; index < strlen(receivedChars); index++){
    delayArray[delayIndex] = receivedChars[index];
    delayIndex ++;
    }

  Serial.print("got through for loop");

  String delayAsString(delayArray);
  int receivedDelay = delayAsString.toInt();
  
  
  Serial.print("Moving forward with a delay of ");
  Serial.print(receivedDelay);

  
  m1.run(FORWARD);
  Serial.print(" actually ran");
  /*m2.run(FORWARD);
  m3.run(FORWARD);
  m4.run(FORWARD);
  */
  delay(receivedDelay);
  
  }




void showNewData() {
    if (newData == true) {
        Serial.print("This just in ... ");
        Serial.println(receivedChars);

        moveMotors();
        newData = false;
    }
}
