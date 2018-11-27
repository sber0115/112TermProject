import serial


arduinoSerialData = serial.Serial('com20',9600)


def moveForward():
    
    arduinoSerialData.write("w".encode())
    arduinoSerialData.write("y".encode())
  
  
def moveBackward():
    
    arduinoSerialData.write("s".encode())
    arduinoSerialData.write("y".encode())

def turnRight():
    arduinoSerialData.write("d".encode())
    arduinoSerialData.write("y".encode())


    #use some constant for the delay of all of these commands --> don't let
    #it be hardcoded by the arduino code itself
def turnLeft():
    arduinoSerialData.write("a".encode())
    arduinoSerialData.write("y".encode())
    





