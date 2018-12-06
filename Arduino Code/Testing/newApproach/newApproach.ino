#include <AFMotor.h>
#include <string.h>

AF_DCMotor m1(1); //motor on lower left
AF_DCMotor m2(2); //motor on lower right
AF_DCMotor m3(3); //motor on upper right
AF_DCMotor m4(4); //motor on upper left


//m1 and m4 left side
//m2 and m3 the right side

//character array that stores this many characters
const byte numChars = 32;
char receivedChars[numChars];

boolean newData = false;

//a 90 degree rotation entails a delay of 280 --> when passing in parameters for the move
//motors function calculate some ratio in the python code such that a turn is executed with the delay


void setup() {
    Serial.begin(9600);
    Serial.println("<Arduino is ready>");

    m1.setSpeed(255);
    m2.setSpeed(255);
    m3.setSpeed(255);
    m4.setSpeed(255);
}

void loop() {

    //the move motors is executed inside the showNewData function only when
    //there actually is newData aka there was a string like this <01100> that was long
    //enough to splice the delay from 
  
    recvWithStartEndMarkers();
    showNewData();
  
    
}


///when the arduino is sent a string with ending and starting markers "<hello>"
//this function only gets what's between the markers
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


////i want to move the motors according to a delay specified within the sent string
// for example the last three characters of <01300> correspond to a 300ms delay for the motors

//i just basiccaly splice the string again and save the delay as an int
//move the motors forward for that much delay

//***********************************all the code works but when the motor stuff i executed all the motors do is buzz

void moveMotors(){
  Serial.print("moving the motors");

  const byte totalNum = 3;
  
  char delayArray[totalNum];
  int delayIndex = 0;

  String receivedString(receivedChars);

  
  for (int index = 2; index < strlen(receivedChars); index++){
    delayArray[delayIndex] = receivedChars[index];
    delayIndex ++;
    }

  String delayAsString(delayArray);
  int receivedDelay = delayAsString.toInt();
  


  //all motors move forward --> car goes straight ahead
  if (receivedString[0] == '1' and receivedString[1] == '1'){
    m1.run(FORWARD);
    m2.run(FORWARD);
    m3.run(FORWARD);
    m4.run(FORWARD);
    
    }


  //all motors move backward
  else if (receivedString[0] == '0' and receivedString[1] == '0'){
    m1.run(BACKWARD);
    m2.run(BACKWARD);
    m3.run(BACKWARD);
    m4.run(BACKWARD);
    
    }
    
  else if (receivedString[0] == '1' and receivedString[1] == '0'){
    m1.run(FORWARD);
    m4.run(FORWARD);
    m2.run(BACKWARD);
    m3.run(BACKWARD);
    
    
    }

    
  else {
    
    m2.run(FORWARD);
    m3.run(FORWARD);
    m1.run(BACKWARD);
    m4.run(BACKWARD);
    
    
    }

  
  Serial.println(receivedDelay);
  delay(receivedDelay);

  m1.run(RELEASE);
  m2.run(RELEASE);
  m3.run(RELEASE);
  m4.run(RELEASE);
  
  }




void showNewData() {
    if (newData == true) {
        Serial.print("This just in ... ");
        Serial.println(receivedChars);

        moveMotors();
        newData = false;
    }
}
