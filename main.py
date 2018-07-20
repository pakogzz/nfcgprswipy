from machine import UART
from machine import RTC
from machine import SPI
from machine import Pin
import time
import sys
import machine
import pycom
import _thread
import utime
import struct
import binascii
import read
import os
import utime

pycom.heartbeat(False)
pycom.nvs_set('p0', 0)
pycom.nvs_set('p1', 0)

				
sim900 = Pin('P22', mode=Pin.OUT)
#off
sim900.value(1)
sim900.value(0)
time.sleep(5)
sim900.value(1)





def nvs_write():
	while True:
		time.sleep(1)
		print('Write.....')
		p = int(pycom.nvs_get('p'))
		pycom.nvs_set('t'+str(p), utime.mktime(utime.gmtime()))
		pycom.nvs_set('d'+str(p), utime.mktime(utime.gmtime()))
		p = p + 1
		pycom.nvs_set('p', p)
		print(pycom.nvs_get('p'))
		
		
def nfc_read():
	read.do_read()
		

def nvs_read():
	while True:
		print('Read.....')
		p = int(pycom.nvs_get('p'))
		c = 0
		while c < p:
			#print("Position No. %d time: $d, data: %d" % (p, pycom.nvs_get('t'+str(p)), pycom.nvs_get('d'+str(p))))
			print("Position No. %d %02x %02x" % (c, pycom.nvs_get('t'+str(c)), pycom.nvs_get('d'+str(c))))
			#print("Position No. %d %d %d" % (c, pycom.nvs_get('t'+str(c)), pycom.nvs_get('d'+str(c))))
			c += 1
		time.sleep(1)

def checkGPRS():
	uart.write('AT+SAPBR=2,1\r')
	while True:	
		if uart.any() > 0:
			s = str(uart.readall(), "utf-8") 
			print(s[15:22])
			print(s)
			if (s[15:22] == '0.0.0.0'):
				uart.write('AT+SAPBR=1,1\r')
				while True:	
					if uart.any() > 0:
						s = str(uart.readall(), "utf-8")
						print(s)
						if (s == '\r\nOK\r\n'):
							return "MODEM_OK"
						else:
							return "MODEM_ERROR"
			else:
				return "MODEM_OK"
				
def sendData(payload):
	uart.write('AT+HTTPACTION=0\r')
	while True:	
		if uart.any() > 6:
			s = str(uart.readall(), "utf-8") 
			print(s[22:25])
			if (s[22:25] == '200'):
				return "MODEM_OK"
			else:
				return "MODEM_ERROR"
		
def modemInit():
	
	sim900.value(0)
	time.sleep(1)
	sim900.value(1)
	time.sleep(10)
	
	uart.readall()
	if (sendATcommandNoEcho('ATE0') != 'MODEM_OK'): error_handler()
	print("Disabled echo")
	
	
	if (sendATcommand('AT+CLTS=1', 'OK') != 'MODEM_OK'): error_handler()
	print("Enabled network time")
	if (sendATcommand('AT', 'OK') != 'MODEM_OK'): error_handler()
	print("AT test ok")
	if (sendATcommandDate() != 'MODEM_OK'): error_handler()	
	print("Date set ok")
	if (sendATcommand('AT+SAPBR=3,1,"Contype","GPRS"', 'OK') != 'MODEM_OK'): error_handler()	
	print("ok")	
	if (sendATcommand('AT+SAPBR=3,1,"APN","wireless.twilio.com"', 'OK') != 'MODEM_OK'): error_handler()	
	print("ok")
	while True:
		if(checkGPRS() == 'MODEM_OK'): 
			return "MODEM_OK"
	
def modemShutdown():
	sim900.value(1)
	sim900.value(0)
	time.sleep(5)
	sim900.value(1)

	

def sendATcommandPOST(payload):
	
	
	#checkGPRS()
	
	if (sendATcommand('AT+HTTPINIT', 'OK') != 'MODEM_OK'): error_handler()
	print("ok")
	if (sendATcommand('AT+HTTPPARA="CID",1', 'OK') != 'MODEM_OK'): error_handler()
	print("ok")
	if (sendATcommand('AT+HTTPPARA="URL","http://4049fd38.ngrok.io"', 'OK') != 'MODEM_OK'): error_handler()	
	print("ok")	
	if (sendData(payload) == 'MODEM_OK'): 
		pycom.nvs_set('p0', int(pycom.nvs_get('t')))
		print("ok")	
	else:
		print ("server offline need to try again later")

	if (sendATcommand('AT+HTTPTERM', 'OK') != 'MODEM_OK'): error_handler()	
	print("ok")
	
def error_handler():
	print('ERROR_HANDLER')
	#machine.reset()

def sendATcommand(c, e):
	print(c)
	uart.write(c+'\r')
	while True:	
		if uart.any() > 0:
			r = uart.readall()
			print(r)
			if (str(r, "utf-8") == '\r\n'+e+'\r\n'):
				return "MODEM_OK"
			else:
				return "MODEM_ERROR"
				
def sendATcommandNoEcho(c):
	print(c)
	uart.write(c+'\r')
	while True:	
		if uart.any() > 0:
			r = uart.readall()
			print(r)
			if (str(r, "utf-8") == 'ATE0\r\r\nOK\r\n'):
				return "MODEM_OK"
			else:
				return "MODEM_ERROR"
			
def sendATcommandDate():
	uart.write('AT+CCLK?'+'\r')
	time.sleep(.1)
	print(".")
	r = uart.readall()
	print(r)
	if (str(r, "utf-8") != '\r\nERROR\r\n'):
		s = str(r, "utf-8") 
		year = int(s[10:12])+2000
		month = int(s[13:15])
		day = int(s[16:18])
		hour = int(s[19:21])
		min = int(s[22:24])
		sec = int(s[25:27])
		print(year)
		print(month)
		print(day)
		rtc.init((year, month, day, hour, min, sec, 0, 0))
		return "MODEM_OK"
	else:
		return "MODEM_ERROR"	

def nvs_transmit():
	while True:
		time.sleep(15)
		
		try:
			os.stat('data.dat')
			exists = True
		except:
			exists = False
	
		if exists:
		
			p0 = int(pycom.nvs_get('p0'))
			p1 = int(pycom.nvs_get('p1'))
			pycom.nvs_set('t', p1)
			
			print (p0)
			print (p1)
			
			#f1 = open('data.dat', 'rb')
			#print(binascii.hexlify(f1.readall()))
			#f1.close()
			
			if p1 > p0:	
			
				
				f1 = open('data.dat', 'rb')
				f1.seek(p0)
				payload = binascii.hexlify(f1.read(p1-p0))
				print(payload)
				f1.close()
				#pycom.nvs_set('p0', p1)				
				time.sleep(2)
				modemInit();
				payload = binascii.hexlify(bytearray(struct.pack('H', 65535))) + payload
				sendATcommandPOST(payload)
				print(payload)
				modemShutdown();

uart = UART(1, baudrate=19200, pins=('P3','P4'))
rtc = RTC()
print(rtc.now())




#_thread.start_new_thread(nvs_write,())
#_thread.start_new_thread(nvs_read,())
_thread.start_new_thread(nvs_transmit,())
_thread.start_new_thread(nfc_read,())

	



