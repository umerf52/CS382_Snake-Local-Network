import socket
import argparse

def main():
	parser = argparse.ArgumentParser(description='Starts the client. ')
	parser.add_argument('ip_adress', nargs=1, default='192.168.10.4')
	parser.add_argument('port', type=int, nargs=1, default=9999)
	args = parser.parse_args()

	host = args.ip_adress[0]
	port = args.port[0]

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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