import socket               # Import socket module
import threading
import argparse

def on_new_client(clientsocket,addr):
	print ('Got connection from', addr)
	while True:
		msg = clientsocket.recv(1024)
		if msg == 'exit':
			break
		print(addr, ' >> ', msg.decode('utf-8'))
		msg = input('SERVER >> ')
		clientsocket.send(msg.encode('utf-8'))
	clientsocket.close()

def main():
	parser = argparse.ArgumentParser(description='Starts the server. ')
	parser.add_argument('ip_adress', nargs=1, default='192.168.10.1')
	parser.add_argument('port', type=int, nargs=1, default=9999)
	parser.add_argument('players', type=int, nargs=1, default=2)

	args = parser.parse_args()
	# print(args.ip_adress)
	# print(args.port)
	# print(args.players)

	s = socket.socket()         # Create a socket object
	host = socket.gethostname() # Get local machine name
	port = args.port[0]                 # Reserve a port for your service.

	print ('Server started!')
	print ('Waiting for clients...')

	s.bind((host, port))        # Bind to the port
	s.listen(1)                 # Now wait for client connection.

	while True:
		c, addr = s.accept()     # Establish connection with client.
		t = threading.Thread(target=on_new_client, args=(c,addr))
		t.daemon = True
		t.start()
	s.close()

if __name__ == '__main__':
    main()