#from games import *
import games, random

print('\t\tWelcome\n')
again = None

while again != 'n':
	players =[]
	num = games.ask_number(question  = 'Cколько игроков участвует?(2-5): ', low=2, high=5)
	
	for i in range(num):
		name = input('Имя игрока: ')
		score = random.randrange(100)+1
		player = games.Player(name, score)
		players.append(player)

	print('\nResults: ')
	for player in players:
		print(player)

	again = games.ask_yes_no('\nAgain? ("y"/"n")')

input('...')