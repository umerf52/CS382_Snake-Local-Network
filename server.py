import socket
import threading
import argparse
import curses
import pickle
import random  # import randint
import time

def on_new_client(clientsocket, addr,player_num):
	print ('Got connection from', addr)
	player_num = str(player_num)
	clientsocket.send(player_num.encode('utf-8'))				# send player number assigned to client



def create_socket():
	host = socket.gethostbyname(socket.gethostname())
	port = 9999

	s = socket.socket()
	s.bind((host, port))
	s.listen()
	print('Server started!')
	return s


def joining_players(current_players, max_players, mainsocket):
	players_threads = []

	while(current_players < max_players):
		c, addr = mainsocket.accept()     								# Establish connection with client.
		thread = threading.Thread(target=on_new_client, args=(c,addr,current_players))
		thread.daemon = True
		thread.start()
		players_threads.append(c)
		current_players = current_players + 1
	print ("all players connected")
	time.sleep(.3)
	return current_players, players_threads


def listen_client_moves(currentplayers):
	data = None
	for p in currentplayers:
		data = p.recv(1024)

		if data != None:
			break
	return data

def get_moves(current_players, max_players, playersthreads):
	moves_threads = []

	#while():



def main():
	# parser = argparse.ArgumentParser(description='Starts the server. ')
	# parser.add_argument('ip_adress', nargs=1, default='192.168.10.4')
	# parser.add_argument('port', type=int, nargs=1, default=9999)
	# parser.add_argument('players', type=int, nargs=1, default=2)
	# args = parser.parse_args()

	#host = socket.gethostbyname(socket.gethostname())
	#port = 9999                 								# Reserve a port for your service.
	max_players = 2
	current_players = 0
	players = []
	positions = []

	#s = socket.socket()         								# Create a socket object
	#s.bind((host, port))        								# Bind to the port
	#s.listen()                 									# Now wait for client connection.
	#print('Server started!')

	s = create_socket()
	print('Waiting for clients...')

	stdscr = curses.initscr()
	max_y, max_x = stdscr.getmaxyx()
	curses.endwin()
	windowsize = []
	windowsize.extend((max_y, max_x))

	#while current_players < max_players:						# Wait for players to join
	#	c, addr = s.accept()     								# Establish connection with client.
	#	t = threading.Thread(target=on_new_client, args=(c,addr,current_players))
	#	t.daemon = True
	#	t.start()
	#	players.append(c)
	#	current_players = current_players + 1
	
	current_players, players = joining_players(current_players, max_players, s)
	time.sleep(.1)

	for p in players:
		msg = 'create_board'
		p.send(msg.encode('utf-8'))


	for p in players:			# send window size to be created for board 
		windowsize_string = pickle.dumps(windowsize)
		p.send(windowsize_string)


	for p in players:
		temp_x = random.randint(0, max_x-1)
		temp_y = random.randint(0, max_y-1)
		temp_tuple = (temp_x, temp_y)
		positions.append(temp_tuple)

	for p in players:
		data_string = pickle.dumps(positions)
		p.send(data_string)

	s.setblocking(0)

	data_lock = threading.Lock()
	while True:
		data = None
		#for p in players:
		with data_lock:
			print('stuck')
			data = players.recv(1024)
			#mutex.release()
			print('recv')

			#if data != None:
			#	break
			
		temp_list = pickle.loads(data)
		pos = temp_list[0]
		print ("pos :" + str(pos))
		key = temp_list[1]
		temp_x = positions[pos][0]
		temp_y = positions[pos][1]
		if key == curses.KEY_RIGHT:
			temp_x = temp_x + 1
		elif key == curses.KEY_UP:
			temp_y = temp_y - 1
		elif key == curses.KEY_LEFT:
			temp_x = temp_x - 1
		else:
			temp_y = temp_y + 1
		positions[pos] = (temp_x, temp_y)

		data_string = pickle.dumps(positions[pos])
		players[pos].send(data_string)

	t.join()
	s.close()

if __name__ == '__main__':
    main()