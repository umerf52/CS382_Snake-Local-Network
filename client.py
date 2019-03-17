import socket
import argparse
import curses
import pickle

# Global variables
positions = []

def create_board(s, player_num):
	data = s.recv(1024)
	winsize = pickle.loads(data)
	sh, sw = winsize[0], winsize[1]
	stdscr = curses.initscr()
	curses.curs_set(0)
	window = curses.newwin(sh, sw, 0, 0)
	window.keypad(1)
	window.timeout(-1)
	data = s.recv(1024)
	global positions
	positions = pickle.loads(data)
	for i in range(len(positions)):
		if i == player_num:
			window.addch(positions[i][1], positions[i][0], curses.ACS_CKBOARD)
			print(positions[i][1], positions[i][0])
		else:
			window.addch(positions[i][1], positions[i][0], '*')
		next_key = window.getch()
	# msg = 'board made'
	# s.send(msg.encode('utf-8'))
	return window, positions


def create_socket():
	host = socket.gethostbyname(socket.gethostname())
	port = 9999

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, port))
	print('Connected to ', host, port)
	return s

def update_board(new_positions, player_num, window):
	global positions
	old_positions = positions
	for i in range(len(positions)):
		if i == player_num:
			window.addch(new_positions[i][1], new_positions[i][0], curses.ACS_CKBOARD)
			window.addch(old_positions[i][1], old_positions[i][0], ' ')
		else:
			window.addch(new_positions[i][1], new_positions[i][0], '*')
			window.addch(old_positions[i][1], old_positions[i][0], ' ')
	positions = new_positions


def main():
	# parser = argparse.ArgumentParser(description='Starts the client. ')
	# parser.add_argument('ip_adress', nargs=1, default='192.168.10.4')
	# parser.add_argument('port', type=int, nargs=1, default=9999)
	# args = parser.parse_args()

	window = None
	player_num = -1
	s = create_socket()

	data = s.recv(1024)
	data = data.decode('utf-8')
	player_num = int(data)

	data = s.recv(1024)
	data = data.decode('utf-8')
	if data == 'create_board':
		global positions
		window, positions = create_board(s, player_num)

	key = window.getch()

	#s.setblocking(0)
	while True:
		next_key = window.getch()
		key = key if next_key == -1 else next_key
		if (next_key == curses.KEY_RIGHT) or (next_key == curses.KEY_LEFT) or (next_key == curses.KEY_UP) or (next_key == curses.KEY_DOWN):
				s.send(str(next_key).encode('utf-8'))
				data = s.recv(1024)
				new_positions = pickle.loads(data)
				update_board(new_positions, player_num, window)

	s.close()

if __name__ == '__main__':
    main()