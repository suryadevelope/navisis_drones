import serial
ser=serial.Serial("/dev/serial0",921600)
print("start")
readedText = ser.readline()
print(readedText)
ser.close()