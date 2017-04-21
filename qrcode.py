import io
import time
import picamera
from PIL import Image
import zbar
import urllib2
import os
from socketIO_client import SocketIO

# >> /etc/rc.local : sudo python /home/pi/TFE/python/qrcode.py &  

hote = '192.168.1.51'
port = 3000

def is_connected():
	try:
		urllib2.urlopen('https://google.be', timeout=1)
		return True
	except urllib2.URLError as err:
		return False

def QRScan():
	i = 0
	print 'start scanning'
	data = ''
	camera = picamera.PiCamera()
	time.sleep(1)
	#camera.start_preview()

	#Create and configure the reader
	scanner = zbar.ImageScanner()
	scanner.parse_config('enable')

	while(data == '' and i < 100):
	
		#Create the in-memory stream
		stream = io.BytesIO()
		camera.capture(stream, format="jpeg")

		#"Rewind" the stream to the beginning so we can read its content
		stream.seek(0)

		pil = Image.open(stream)
		pil = pil.convert('L')
		width, height = pil.size
		raw = pil.tobytes()

		#wrap image data
		image = zbar.Image(width, height, 'Y800', raw)
	
		#Scan the image
		scanner.scan(image)

		#extract the result
		for symbol in image:
			data = symbol.data
			return data
			camera.close()

		#clean up
		del(image)
		i = i + 1


insist = 0
conn = False
while(insist < 5 and not conn):
	print 'test connection..'
	conn = is_connected()
	time.sleep(1)
	insist = insist + 1

if(conn):
	print 'connected'
	#os.system('cd /home/pi/TFE/source/camera && sudo nodejs app.js &')
else:
	print 'not connected'
	os.system('sudo ifdown wlan0')
	scan = QRScan()
	print 'data : '+scan

	mot = 0
	userID = ''
	ssid = ''
	password = ''

	for lettre in scan:
		if lettre in ' ':
			print 'nouveau mot'
			mot = mot + 1
		else:
			if(mot == 0):
				userID = userID + lettre
			else:
				if(mot == 1):
					ssid = ssid + lettre
				else:
					password = password + lettre

	cmd1 = '''network={
	ssid="''' + ssid + '''"
	psk="''' + password + '''"
	key_mgmt=WPA-PSK
}'''
	cmd = 'sudo echo \'' + cmd1 + '\' >> /etc/wpa_supplicant/wpa_supplicant.conf'
	os.system(cmd)
	time.sleep(1)
	os.system('sudo ifup wlan0')
	

	insist = 0
	conn = False
	while(insist < 15 and not conn):
		conn = is_connected()
		time.sleep(1)
		print 'test connection..'
		insist = insist + 1

	if(conn):
		socket = SocketIO(hote,port)
		p = os.popen('cat /proc/cpuinfo | grep Serial | cut -d ":" -f 2')
		serial = p.readline()
		print serial
		socket.emit('newCameraConnection',{'userID': userID, 'serial': serial})
		time.sleep(1)
		#os.system("sudo cd /home/pi/TFE/source/camera && sudo nodejs app.js &")
	else:
		print 'fail connection'	
	
