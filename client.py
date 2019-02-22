import socket
import argparse

def main():
	parser = argparse.ArgumentParser(description='Starts the client. ')
	parser.add_argument('ip_adress', nargs=1, default='192.168.10.1')
	parser.add_argument('port', type=int, nargs=1, default=9999)

	args = parser.parse_args()
	# print(args.ip_adress)

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	host = socket.gethostname()
	port = args.port[0]

	s.connect((host, port))
	print('Connected to ', host, port)

	while True:
		msg = input()
		if msg == 'exit':
			break
		s.send(msg.encode('utf-8'))
		msg = s.recv(1024)
		print(msg.decode('utf-8'))
	s.close()

if __name__ == '__main__':
    main()