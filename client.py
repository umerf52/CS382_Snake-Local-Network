# References:
# https://github.com/KyrosDigital/SnakeGame
# https://github.com/engineer-man/youtube/tree/master/015

import socket
import argparse
import curses
import pickle
import random
import time

# Global variables
positions = []
snakes = []
SNAKE_LENGTH = 5

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
	window.border(0)
	data = s.recv(1024)
	global positions
	positions = pickle.loads(data)
	for i in range(len(positions)):
		temp_snake = []
		for j in range(0, -1*SNAKE_LENGTH, -1):
			temp_snake.append((positions[i][1], positions[i][0]-j))
		global snakes
		snakes.append(temp_snake)
		if i == player_num:
			for j in range(0, SNAKE_LENGTH):
				window.addch(snakes[i][j][0], snakes[i][j][1], curses.ACS_BLOCK)
		
		else:
			for j in range(0, SNAKE_LENGTH):
				window.addch(snakes[i][j][0], snakes[i][j][1], curses.ACS_CKBOARD)
				
	return window, positions, sh, sw


def create_socket(ip_adress, port):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((ip_adress, port))
	print('Connected to ', ip_adress, port, '\nWaiting for other players.\n')
	return s

def update_board(new_positions, player_num, window):
	window.clear()
	window.border(0)
	global snakes
	
	for i in range(len(new_positions)):
		snakes[i].pop()
		new_head = (new_positions[i][1], new_positions[i][0])
		snakes[i].insert(0, new_head)
		
		if i == player_num:
			for j in range(0, SNAKE_LENGTH):
				window.addch(snakes[i][j][0], snakes[i][j][1], curses.ACS_BLOCK)
		else:
			if (new_positions[i][1] != -1) and (new_positions[i][0] != -1):
				for j in range(0, SNAKE_LENGTH):
					window.addch(snakes[i][j][0], snakes[i][j][1], curses.ACS_CKBOARD)

	head_x = snakes[player_num][0][1]
	head_y = snakes[player_num][0][0]
	global positions
	for i in range(len(positions)):
		if i != player_num:
			for j in range(SNAKE_LENGTH):
					if snakes[i][j][0] == head_y and snakes[i][j][1] == head_x:
						msg = 'Head to body collision detected'
						return msg

	positions = new_positions
	return None


def main():
	parser = argparse.ArgumentParser(description='Starts the client. ')
	parser.add_argument('ip_adress', nargs=1, default='192.168.10.4')
	parser.add_argument('port', type=int, nargs=1, default=9999)
	args = parser.parse_args()

	player_num = -1
	window = None
	max_x = 0
	max_y = 0
	key_list = [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]
	key = -1

	s = create_socket(args.ip_adress[0], args.port[0])
	# s = create_socket(socket.gethostbyname(socket.gethostname()), 9999)

	data = s.recv(1024)
	data = data.decode('utf-8')
	player_num = int(data)

	data = s.recv(1024)
	data = data.decode('utf-8')
	if data == 'create_board':
		s.send('started making board'.encode('utf-8'))
		global positions
		window, positions, max_y, max_x = create_board(s, player_num)

	y_ratio = float(positions[player_num][1]) / max_y
	x_ratio = float(positions[player_num][0]) / max_x

	if (y_ratio < 0.5) and (x_ratio < 0.5):
		key = random.choice([key_list[1], key_list[3]])
	elif (y_ratio < 0.5) and (x_ratio >= 0.5):
		key = random.choice([key_list[1], key_list[2]])
	elif (y_ratio >= 0.5) and (x_ratio < 0.5):
		key = random.choice([key_list[0], key_list[3]])
	else:
		key = random.choice([key_list[0], key_list[2]])

	temp = None
	while True:
		next_key = window.getch()
		time.sleep(0.005)

		if next_key != -1:
			key = next_key
		try:
			if key in key_list:
				if temp != None:
					s.send(str(temp).encode('utf-8'))
				else:
					s.send(str(key).encode('utf-8'))
				data = s.recv(1024)
				response = pickle.loads(data)

				if response == 'You won!':
					print(response)
					window.clear()
					curses.endwin()
					break

				if response == 'Head to Head collision detected.':
					window.clear()
					print(response, '\nGAME OVER.')
					curses.endwin()
					break

				if response == 'Head to body collision detected':
					print(response, '\nGAME OVER.')
					curses.endwin()
					break

				if response == 'Out of bounds. ':
					print(response, '\nGAME OVER.')
					curses.endwin()
					break

				temp = update_board(response, player_num, window)
		except socket.error:
			print ('GAME OVER.')

	s.close()

if __name__ == '__main__':
    main()