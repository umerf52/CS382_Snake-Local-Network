import socket
import threading
import argparse
import curses
import pickle
import random  # import randint
import time

# Global variables
positions = []

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
	print ("\nAll players connected\n")
	return current_players, players_threads


def listen_client_moves(player_num, s, players, max_x, max_y, current_players):
	flag = False
	while True:
		data = s.recv(1024)
		key = int(data.decode('utf-8'))

		global positions
		temp_x = positions[player_num][0]
		temp_y = positions[player_num][1]

		if key == curses.KEY_RIGHT:
			temp_x = temp_x + 1
		elif key == curses.KEY_UP:
			temp_y = temp_y - 1
		elif key == curses.KEY_LEFT:
			temp_x = temp_x - 1
		else:
			temp_y = temp_y + 1

		if (temp_x >= max_x-1) or (temp_x <= 0) or (temp_y >= max_y-1) or (temp_y <= 0):
			s.send(pickle.dumps('Out of bounds. '))
			positions[player_num] = (-1, -1)
			current_players -= 1
			s.close()
			flag = True
			break

		for i in range(len(positions)):
			if i == player_num:
				continue
			else:
				if (temp_x == positions[i][0]) and (temp_y == positions[i][1]):
					msg = 'Collision detected.'
					s.send(pickle.dumps(msg))
					players[i].send(pickle.dumps(msg))
					current_players -= 2
					s.close()
					players[i].close()
					flag = True
					break

		if flag == True:
			break
		positions[player_num] = (temp_x, temp_y)

		data_string = pickle.dumps(positions)
		s.send(data_string)

	return


def main():
	# parser = argparse.ArgumentParser(description='Starts the server. ')
	# parser.add_argument('ip_adress', nargs=1, default='192.168.10.4')
	# parser.add_argument('port', type=int, nargs=1, default=9999)
	# parser.add_argument('players', type=int, nargs=1, default=2)
	# args = parser.parse_args()

	max_players = 2
	current_players = 0
	players = []

	s = create_socket()
	print('Waiting for clients... \n')

	stdscr = curses.initscr()
	max_y, max_x = stdscr.getmaxyx()
	curses.endwin()
	max_y = max_y-2
	max_x = max_x-2
	window_size = (max_y, max_x)
	
	current_players, players = joining_players(current_players, max_players, s)

	for p in players:
		msg = 'create_board'
		p.send(msg.encode('utf-8'))
		data = p.recv(1024)
		msg = data.decode('utf-8')
		if msg == 'started making board':
			# print(msg)
			continue
		else:
			print('Error issuing create_board')


	for p in players:			# send window size to be created for board 
		# window_size_string = pickle.dumps(window_size)
		p.send(pickle.dumps(window_size))
		data = p.recv(1024)
		msg = data.decode('utf-8')
		if msg == 'size received':
			# print(msg)
			continue
		else:
			print('Error sending size')


	for p in players:
		temp_x = random.randint(0, max_x-1)
		temp_y = random.randint(0, max_y-1)
		temp_tuple = (temp_x, temp_y)
		positions.append(temp_tuple)


	for p in players:
		data_string = pickle.dumps(positions)
		p.send(data_string)


	listener_threads = []
	for i in range(len(players)):
		thread = threading.Thread(target=listen_client_moves, args=(i, players[i], players, max_x, max_y, current_players))
		thread.daemon = True
		thread.start()
		listener_threads.append(thread)


	while True:
		flag = False
		for thread in listener_threads:
			if thread.isAlive():
				flag = True

		if flag == False:
			break


	s.close()
	print('All players disconnected. \nShutting down server.')

if __name__ == '__main__':
    main()