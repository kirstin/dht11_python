import RPi.GPIO as GPIO
import time, sys, traceback

def bin2dec(string_num):
    return str(int(string_num, 2))

data = []

GPIO.setmode(GPIO.BCM)

GPIO.setup(4,GPIO.OUT)
GPIO.output(4,GPIO.HIGH)
time.sleep(0.025)
GPIO.output(4,GPIO.LOW)
time.sleep(0.02)

GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

for i in range(0,3000):
    data.append(GPIO.input(4))

#print(data)

bit_count = 0
count = 0
HumidityBit = ""
TemperatureBit = ""
HumidityRat = ""
TemperatureRat = ""
crc = ""
stream = []
sum = 0
average = 0

while count < len(data):
	# write the length of each block of 1s into a list
	# if we read more than 70 1s in a row, we most likely
	# reached the end or the data is corrupted
	if bit_count > 70:
	        break
	bit_count = 0
	while data[count] == 0:
         	count = count + 1
		if count >= len(data):
                       	break
	if count >= len(data):
		break
        while data[count] == 1:
               	bit_count = bit_count + 1
            	count = count + 1
		if count >= len(data):
                      	break
		if bit_count > 70:
			break
	stream.append(bit_count)
	sum = sum + bit_count
	
average = sum/len(stream)
#print("******")
#print(stream)
#print(len(stream))
#print("Average length: " + str(average))

# the stream should have a length of 42 (40 data bits + 1s at beginning and end)
# if it doesn't, something went wrong
if len(stream) == 42:
	stream = stream[1:41]
else:
	print("ERROR: Data coppupted or not enough read.\nTry again. If this happens repeatedly:\nIs the sensor connected correctly?")
	GPIO.cleanup()
	exit(0)

bit_pos=0
for number in stream:
	# interpret blocks of 1s as 1 or 0 and place in correct container
	if number > average:
		if bit_pos>=0 and bit_pos<8:
			HumidityBit = HumidityBit + "1"
		if bit_pos>=8 and bit_pos<16:
			HumidityRat = HumidityRat + "1"
		if bit_pos>=16 and bit_pos<24:
			TemperatureBit = TemperatureBit + "1"
		if bit_pos>=24 and bit_pos<32:
			TemperatureRat = TemperatureRat + "1"
		if bit_pos>=32 and bit_pos<40:
			crc = crc + "1"
	else:
		if bit_pos>=0 and bit_pos<8:
			HumidityBit = HumidityBit + "0"
		if bit_pos>=8 and bit_pos<16:
                        HumidityRat = HumidityRat + "0"
		if bit_pos>=16 and bit_pos<24:
			TemperatureBit = TemperatureBit + "0"
		if bit_pos>=24 and bit_pos<32:
                        TemperatureRat = TemperatureRat + "0"
		if bit_pos>=32 and bit_pos<40:
			crc = crc + "0"
	bit_pos = bit_pos + 1

Humidity = bin2dec(HumidityBit)
Temperature = bin2dec(TemperatureBit)
h = bin2dec(HumidityRat)
t = bin2dec(TemperatureRat)

# do checksum and print result
if int(Humidity) + int(Temperature) - int(bin2dec(crc)) == 0:
	print "Humidity:"+ Humidity + "." + h +"%"
	print "Temperature:"+ Temperature + "." + t +"C"
else:
        print("Hum: " + Humidity)
        print("Temp: " + Temperature)
	print "ERR_CRC"
GPIO.cleanup()
