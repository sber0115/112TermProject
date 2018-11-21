#include <AFMotor.h>

AF_DCMotor m1(1);
AF_DCMotor m2(2);
AF_DCMotor m3(3);
AF_DCMotor m4(4);
int state = 0;
unsigned long lastMsg = 0;

void setup() {
  // put your setup code here, to run once:

  Serial.begin(9600);
  Serial.println("Motor test!");

  m1.setSpeed(255);
  m2.setSpeed(255);
  m3.setSpeed(255);
  m4.setSpeed(255);
}

void loop() 
{
    // Checks whether data is comming from the serial port
    if(Serial.available() > 0)
    { 
        state = Serial.read(); // Reads the data from the serial port
        lastMsg = millis();
    }
    
 
    if (state == 'w') 
    {
        m1.run(FORWARD);
        m2.run(FORWARD);
        m3.run(FORWARD);
        m4.run(FORWARD);
    }
    else if (state == 's')
    {
        m1.run(BACKWARD);
        m2.run(BACKWARD);
        m3.run(BACKWARD);
        m4.run(BACKWARD);
    }
    else if (state == 'a')
    {
        m1.run(BACKWARD);
        m2.run(FORWARD);
        m3.run(FORWARD);
        m4.run(BACKWARD);
    }
    else if (state == 'd')
    {
        m1.run(FORWARD);
        m2.run(BACKWARD);
        m3.run(BACKWARD);
        m4.run(FORWARD);
    }
    else
    {
        m1.run(RELEASE);
        m2.run(RELEASE);
        m3.run(RELEASE);
        m4.run(RELEASE);
    } 

}
