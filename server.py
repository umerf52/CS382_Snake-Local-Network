import socket
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
	parser.add_argument('ip_adress', nargs=1, default='192.168.10.4')
	parser.add_argument('port', type=int, nargs=1, default=9999)
	parser.add_argument('players', type=int, nargs=1, default=2)
	args = parser.parse_args()

	host = args.ip_adress[0]
	port = args.port[0]                 # Reserve a port for your service.
	max_players = args.players[0]
	current_players = 0
	players = []

	s = socket.socket()         # Create a socket object
	s.bind((host, port))        # Bind to the port
	s.listen()                 # Now wait for client connection.
	print('Server started!')
	print('Waiting for clients...')

	while current_players < max_players:						# Wait for players to join
		c, addr = s.accept()     # Establish connection with client.
		current_players = current_players + 1
		t = threading.Thread(target=on_new_client, args=(c,addr))
		t.daemon = True
		t.start()
		players.append(t)

	s.close()

if __name__ == '__main__':
    main()