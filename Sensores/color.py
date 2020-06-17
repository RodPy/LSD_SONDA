#rpi serial connections
#Python app to run a S8 Sensor
import serial
import time

# RPi pin connextions:
#pin 6	GND
#pin 4	5v
#pin 8	TXD:  UART data to S8
#pin 10  RXD: UART data from S8

ser = serial.Serial("/dev/ttyS0",baudrate =9600,timeout = .5)
print " Raspberry Pi3 to COLOR Via UART\n"
time.sleep(1)


ser.write("R")
esp = ser.read(30)

print esp
time.sleep(1.9)

