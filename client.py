import socket
import argparse
import curses
import pickle
import random

# Global variables
positions = []
#snake = [[0,0], [0,0], [0,0]]


def create_board(s, player_num):
	data = s.recv(1024)
	winsize = pickle.loads(data)
	s.send('size received'.encode('utf-8'))
	sh, sw = winsize[0], winsize[1]
	stdscr = curses.initscr()
	curses.curs_set(0)
	window = curses.newwin(sh, sw, 0, 0)
	window.keypad(1)
	window.timeout(1)
	data = s.recv(1024)
	global positions
	positions = pickle.loads(data)
	for i in range(len(positions)):
		if i == player_num:
			window.addch(positions[i][1], positions[i][0], curses.ACS_CKBOARD)
			window.addch(positions[i][1], positions[i][0]-1, curses.ACS_CKBOARD)
			window.addch(positions[i][1], positions[i][0]-2, curses.ACS_CKBOARD)
		else:
			window.addch(positions[i][1], positions[i][0], '*')
			#window.addch(positions[i][1], positions[i][0]-1, '*')
			#window.addch(positions[i][1], positions[i][0]-2, '*')
		next_key = window.getch()
	return window, positions


def create_socket():
	host = socket.gethostbyname(socket.gethostname())
	port = 9999

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, port))
	print('Connected to ', host, port, '\n')
	return s

def update_board(new_positions, player_num, window):
	window.clear()
	for i in range(len(new_positions)):
		if i == player_num:
			window.addch(new_positions[i][1], new_positions[i][0], curses.ACS_CKBOARD)
			window.addch(new_positions[i][1], new_positions[i][0]-1, curses.ACS_CKBOARD)
			window.addch(new_positions[i][1], new_positions[i][0]-2, curses.ACS_CKBOARD)
		else:
			if (new_positions[i][1] != -1) and (new_positions[i][0] != -1):
				window.addch(new_positions[i][1], new_positions[i][0], '*')
				#window.addch(new_positions[i][1], new_positions[i][0]-1, '*')
				#window.addch(new_positions[i][1], new_positions[i][0]-2, '*')


	global positions
	positions = new_positions


def main():
	# parser = argparse.ArgumentParser(description='Starts the client. ')
	# parser.add_argument('ip_adress', nargs=1, default='192.168.10.4')
	# parser.add_argument('port', type=int, nargs=1, default=9999)
	# args = parser.parse_args()

	player_num = -1
	window = None
	key_list = [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]

	s = create_socket()

	data = s.recv(1024)
	data = data.decode('utf-8')
	player_num = int(data)

	data = s.recv(1024)
	data = data.decode('utf-8')
	if data == 'create_board':
		s.send('started making board'.encode('utf-8'))
		global positions
		window, positions = create_board(s, player_num)

	key = random.choice(key_list)

	while True:
		next_key = window.getch()
		if next_key == -1:
			key = key
		else:
			key = next_key
		if key in key_list:
			s.send(str(key).encode('utf-8'))
			data = s.recv(1024)
			response = pickle.loads(data)
			if response == 'You Won':
				print(response, '\nGAME OVER.')
				curses.endwin()
				break

			if response == 'Collision detected.':
				print(response, '\nGAME OVER.')
				curses.endwin()
				break

			if response == 'Out of bounds. ':
				print(response, '\nGAME OVER.')
				curses.endwin()
				break

			update_board(response, player_num, window)
		else:
			update_board(positions, player_num, window)

	s.close()

if __name__ == '__main__':
    main()