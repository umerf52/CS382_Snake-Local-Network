import socket
import argparse
import curses
import pickle

def create_board(s, player_num):
	data = s.recv(1024)
	positions = pickle.loads(data)
	stdscr = curses.initscr()
	# curses.curs_set(0)
	sh, sw = stdscr.getmaxyx()
	window = curses.newwin(sh, sw, 0, 0)
	window.keypad(1)
	window.timeout(-1)
	for i in range(len(positions)):
		if i == player_num:
			window.addch(positions[i][1], positions[i][0], curses.ACS_CKBOARD)
		else:
			window.addch(positions[i][1], positions[i][0], curses.ACS_PI)
		next_key = window.getch()
	return window

def main():
	# parser = argparse.ArgumentParser(description='Starts the client. ')
	# parser.add_argument('ip_adress', nargs=1, default='192.168.10.4')
	# parser.add_argument('port', type=int, nargs=1, default=9999)
	# args = parser.parse_args()

	host = '192.168.10.2'
	port = 9999
	window = None
	player_num = -1

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, port))
	# s.setblocking(0)
	print('Connected to ', host, port)

	data = s.recv(1024)
	data = data.decode('utf-8')
	player_num = int(data)

	data = s.recv(1024)
	data = data.decode('utf-8')
	if data == 'create_board':
		window = create_board(s, player_num)
	window.nodelay(False)

	while True:
		next_key = window.getch()
		# print(next_key)
		# curses.endwin()
		if (next_key == curses.KEY_RIGHT) or (next_key == curses.KEY_LEFT) or (next_key == curses.KEY_UP) or (next_key == curses.KEY_DOWN):
				temp_list = []
				temp_list.append(player_num)
				temp_list.append(next_key)
				data_string = pickle.dumps(temp_list)
				s.send(data_string)

				data = s.recv(1024)
				new_pos = pickle.loads(data)
				window.addch(new_pos[0], new_pos[1], curses.ACS_CKBOARD)



		# msg = input()
		# if msg == 'exit':
		# 	break
		# s.send(msg.encode('utf-8'))
		# msg = s.recv(1024)
		# print(msg.decode('utf-8'))
		# msg = input()

	s.close()

if __name__ == '__main__':
    main()