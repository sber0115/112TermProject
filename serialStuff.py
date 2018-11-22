import serial


arduinoSerialData = serial.Serial('com20',9600)


def moveForward():
    
    arduinoSerialData.write("w".encode())
    arduinoSerialData.write("a".encode())
  
  
def moveBackward():
    
    arduinoSerialData.write("s".encode())
    arduinoSerialData.write("a".encode())
    





