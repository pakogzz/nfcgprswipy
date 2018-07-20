import mfrc522
from os import uname
import pycom
import utime
import struct
import time
from machine import Pin

def do_read():

	buzzer = Pin('P21', mode=Pin.OUT)
	
	if uname()[0] == 'WiPy':
		rdr = mfrc522.MFRC522("P10", "P11", "P14", "P20", "P19")
	elif uname()[0] == 'esp8266':
		rdr = mfrc522.MFRC522(0, 2, 4, 5, 14)
	else:
		raise RuntimeError("Unsupported platform")

	print("")
	print("Place card before reader to read from address 0x08")
	print("")

	try:
		while True:

			(stat, tag_type) = rdr.request(rdr.REQIDL)

			if stat == rdr.OK:

				(stat, raw_uid) = rdr.anticoll()

				if stat == rdr.OK:
					pycom.rgbled(0xff0000)
					buzzer.value(1)
					print("New card detected")
					print("  - tag type: 0x%02x" % tag_type)
					print("  - uid	 : 0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
					print("")
					del raw_uid[-1]
					
					t = utime.mktime(utime.gmtime())
					d = struct.unpack('I', bytearray(raw_uid))[0]
					
					print ("Time: %d" % (t))
					print ("Data: %d" % (d))
					
					p1 = int(pycom.nvs_get('p1'))
					
					pycom.rgbled(0x000000)
					buzzer.value(0)
					
					if p1 >= 262144:
						p1 = 0
						pycom.nvs_set('p1', 0)
					
					f = open('data.dat', 'ab')
					f.seek(p1)
					f.write(bytes(struct.pack('I', t)))
					f.write(bytes(raw_uid))
					f.close()
					p1 += 8
					pycom.nvs_set('p1', p1)	
					'''
					t = utime.mktime(utime.gmtime())
					d = struct.unpack('I', bytearray(raw_uid))[0]
					
					print ("Time: %d" % (t))
					print ("Data: %d" % (d))
					
					p = int(pycom.nvs_get('p'))
					pycom.nvs_set('t'+str(p), t)
					pycom.nvs_set('d'+str(p), d)
					p = p + 1
					pycom.nvs_set('p', p)
					print ("Seq: %d" % (pycom.nvs_get('p')))
					'''
			
					'''
					if rdr.select_tag(raw_uid) == rdr.OK:

						key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

						if rdr.auth(rdr.AUTHENT1A, 8, key, raw_uid) == rdr.OK:
							print("Address 8 data: %s" % rdr.read(8))
							rdr.stop_crypto1()
						else:
							print("Authentication error")
					else:
						print("Failed to select tag")
					'''
					
	except KeyboardInterrupt:
		print("Bye")