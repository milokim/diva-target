import os
import socket
import sys
import subprocess
import threading
import time

class TargetThread(object):
	def __init__(self, user, host, port, timeout):
		self.user = user
		self.host = host
		self.port = port
		self.duration = timeout

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.bind((self.get_ip(), port))

	def get_ip(self):
		return os.popen('/sbin/ifconfig eth0 | grep "inet\ addr" | cut -d: -f2 | cut -d" " -f1').read()

	def clean_files(self):
		os.system("rm log.txt")

	# Get device information and save it as a file
	def device_info(self):
		f = open("device.txt", 'w')
		self._exec("uname -rms", f)
		self._exec("lsb_release -idrc", f)

	def listen(self):
		self.sock.listen(1)
		while True:
			conn, addr = self.sock.accept()
			print ("Connected from " + str(addr))
			threading.Thread(target = self.recv_thread,args = (conn,addr)).start()

	def recv_thread(self, conn, addr):
		while True:
			data = conn.recv(32).decode()

			if data == "job:1":
				print "Reboot request"
				self.clean_files()
				self.device_info()
				time.sleep(1)	# make sure fwrite operation prior to reboot
				self.exec_reboot()
			elif data == "job:2":
				print "Run Dogtail test"
				self.clean_files()
				self.start_timer(True)
				self.device_info()
				self.exec_dogtail()
			elif data == "job:3":
				print "Run OPENGL test"
				self.clean_files()
				self.start_timer(True)
				self.device_info()
				self.exec_opengl()

			time.sleep(1)
	
		conn.close()

	def start_timer(self, terminated):
		timeout = self.duration + 5
		if terminated is True:
			threading.Timer(timeout, self.timer_expired, ["terminated"]).start()
		else:
			threading.Timer(timeout, self.timer_expired).start()

	# When timer is expired, terminate running process and transfer output files
	def timer_expired(self, arg):
		if arg == "terminated":
			self.pid.terminate()

		dest = self.user + "@" + self.host + ":/home/" + self.user + "/output/"
		self._exec("scp device.txt " + dest, None)

		# Send log file if created
		if os.path.isfile("log.txt") is True:
			self._exec("scp log.txt " + dest, None)

		print "Done!"

	# Run dogtail and save output
	def exec_dogtail(self):
		f = open("log.txt", 'w')
		self._exec("python dogtail_unit_test/gedit.py", f)

	# Run glmark2 and save output
	def exec_opengl(self):
		f = open("log.txt", 'w')
		self._exec("glmark2-es2 -s 1920x1280", f)

	def exec_reboot(self):
		self._exec("sudo shutdown -r now", None)

	def _exec(self, args, f):
		out = args.split(' ')

		if f is None:
			self.pid = subprocess.Popen(out)
		else:
			self.pid = subprocess.Popen(out, stdout=f)

def help():
	print """
	Available options

	-u	username.
	-s	DIVA server hostname or ip.
	-p	port number.
	-t	Timeout for unit test (unit is seconds)

	Example: python dthread.py -u diva -s diva-server -p 3505 -t 120
	""";

if __name__ == '__main__':
	options = sys.argv

	# Default values
	user = 'diva'
	host = 'diva-server'
	port = 3505
	duration = 120	#unit is seconds

	# Help - not host ;)
	if '-h' in options:
		help()
		exit()

	if '-u' in options:
		index = options.index('-u') + 1
		user = options[index]

	if '-s' in options:
		index = options.index('-s') + 1
		host = options[index]

	if '-p' in options:
		index = options.index('-p') + 1
		port = int(options[index])

	if '-t' in options:
		index = options.index('-t') + 1
		duration = int(options[index])

	TargetThread(user, host, port, duration).listen()
