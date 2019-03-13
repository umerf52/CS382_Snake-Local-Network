import socket
import argparse
import curses
import pickle

def create_board(s, player_num):
	data = s.recv(1024)
	winsize = pickle.loads(data)
	sh, sw = winsize[0], winsize[1]
	data = s.recv(1024)
	positions = pickle.loads(data)
	stdscr = curses.initscr()
	curses.curs_set(0)
	window = curses.newwin(sh, sw, 0, 0)
	window.keypad(1)
	window.timeout(-1)
	for i in range(len(positions)):
		if i == player_num:
			window.addch(positions[i][1], positions[i][0], curses.ACS_CKBOARD)
			print(positions[i][1], positions[i][0])
		else:
			window.addch(positions[i][1], positions[i][0], '*')
		next_key = window.getch()
	return window, positions


def create_socket():
	host = socket.gethostbyname(socket.gethostname())
	port = 9999

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, port))
	##s.listen()
	print('Connected to ', host, port)
	return s


def main():
	# parser = argparse.ArgumentParser(description='Starts the client. ')
	# parser.add_argument('ip_adress', nargs=1, default='192.168.10.4')
	# parser.add_argument('port', type=int, nargs=1, default=9999)
	# args = parser.parse_args()

	#host = socket.gethostbyname(socket.gethostname())
	#port = 9999
	window = None
	player_num = -1

	positions = []

	#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#s.connect((host, port))
	# s.setblocking(0)
	#print('Connected to ', host, port)
	s = create_socket()

	data = s.recv(1024)
	data = data.decode('utf-8')
	player_num = int(data)

	print ("player number: " + str(player_num))
	data = s.recv(1024)
	data = data.decode('utf-8')
	if data == 'create_board':
		window, positions = create_board(s, player_num)

	window.nodelay(False)
	key = window.getch()
	window.nodelay(True)

	#s.setblocking(0)
	while True:
		next_key = window.getch()
		key = key if next_key == -1 else next_key
		if (next_key == curses.KEY_RIGHT) or (next_key == curses.KEY_LEFT) or (next_key == curses.KEY_UP) or (next_key == curses.KEY_DOWN):
				temp_list = []
				temp_list.append(player_num)
				temp_list.append(next_key)
				data_string = pickle.dumps(temp_list)
				print ("input sent")
				s.send(data_string)

				print ("input received")
				data = s.recv(1024)
				new_pos = pickle.loads(data)
				print(new_pos[1], new_pos[0])
				window.addch(positions[player_num][1], positions[player_num][0], ' ')
				positions[player_num] = (new_pos[0], new_pos[1])
				window.addch(new_pos[1], new_pos[0], curses.ACS_CKBOARD)

	s.close()

if __name__ == '__main__':
    main()