#Блек-джек
#от 1 до 7 игроков
import cards, games
from os import *

class BJ_Card(cards.Card):
	"""Карта для игры в блек джек"""
	ACE_VALUE = 1
	@property
	def value(self):
		if self.is_face_up:
			v = BJ_Card.RANKS.index(self.rank) + 1
			if v > 10:
				v = 10
		else:
				v = None
		return v


class BJ_Deck(cards.Deck):
	"""Колода для игры в Блек джек"""
	def populate(self):
		for suit in BJ_Card.SUITS:
			for rank in BJ_Card.RANKS:
				self.cards.append(BJ_Card(rank, suit))

	@property #возвращает количество оставшихся карт
	def ostatok(self):
		return len(self.cards)



class BJ_Hand(cards.Hand):
	"""'Рука': набор карт у одного игрока"""
	def __init__(self, name, credits = 500):
		super(BJ_Hand,self).__init__()
		self.name = name
		self.credits = credits

	def __str__(self):
		rep = self.name + ':\t' + super(BJ_Hand, self).__str__()
		if self.total:
			rep += '(' + str(self.total) + ')'

		if self.credits:
			rep += '\t' + 'credits: ' + str(self.credits)
		return rep

	def stavka(self, stavka):
		"""вычитает из кредита игрока размер ставки"""
		self.credits -= stavka

	@property
	def total(self):
		#eсли у одной из карт value равно None, то и все свойство равно None
		for card in self.cards:
			if not card.value:
				return None

		#суммируем все очки считая туз за 1 очко
		t = 0
		for card in self.cards:
			t += card.value

		#определяем есть ли туз на руках у игроков
		contains_ace = False
		for card in self.cards:
			if card.value == BJ_Card.ACE_VALUE:
				contains_ace = True

		#если на руках есть туз и сумма очков не превышает 11, будем считать туз за 11 очков
		if contains_ace and t <= 11:
			#прибавить нужно лишь 10, потому что 1 уже вошла в общую сумму
			t+=10
		return t 

	def is_busted(self):
		return self.total > 21


class BJ_Player(BJ_Hand):
	"""Игрок в блек джек"""
	def is_hitting(self):
		response = games.ask_yes_no('\n' + self.name + ' будете брать еще карты? (y/n) ')
		return response == 'y'

	def bust(self):
		print(self.name, "перебрал")
		self.lose()

	def lose(self):
		print(self.name, "проиграл")

	def win(self):
		print(self.name, "выиграл")

	def push(self):
		print(self.name, "сыграл в ничью")


class BJ_Dealer(BJ_Hand):
	"""Дилер в игре блек джек"""
	def is_hitting(self):
		return self.total < 17

	def bust(self):
		print(self.name, "перебрал")

	def flip_first_card(self):
		first_card = self.cards[0]
		first_card.flip()


class BJ_Game(object):
	"""Игра в блек джек"""
	def __init__(self, names):
		self.players = []
		for name in names:
			player = BJ_Player(name)
			self.players.append(player)
		self.dealer = BJ_Dealer('Dealer')
		self.deck = BJ_Deck()
		self.deck.populate()
		self.deck.shuffle()
		self.kon = 0 #кон стола
		self.stavka = 100 #фиксированная ставка каждый раунд


	@property
	def still_playing(self):
		sp =[]
		for player in self.players:
			if not player.is_busted():
				sp.append(player)
		return sp

	def __additional_cards(self, player):
		while not player.is_busted() and player.is_hitting():
			self.deck.deal([player])
			print(player)
			if player.is_busted():
				player.bust()

	def reload_deck(self):
		"""Если в колоде меньше 30 карт, то обновим колоду"""
		if  self.deck.ostatok < 30:
			self.deck.cards = []
			self.deck.populate()
			self.deck.shuffle()

	def isBankrot(self):
		'''Если игрок банкрот'''
		for player in self.players:
			if player.credits <= 0:
				print('\nИгрок {} покинул игру так как стал Банкротом'.format(player.name))
				self.players.remove(player)


	def play(self):	
		#проверка на банкрота
		self.isBankrot()
		#игроки и дилер делают ставки	
		for player in self.players:
			player.stavka(self.stavka)
			self.kon += self.stavka
		self.dealer.stavka(self.stavka)
		self.kon += self.stavka
		print('На кону {} кредитов\n'.format(self.kon))
		#сдача по две карты
		self.deck.deal(self.players + [self.dealer], per_hand = 2)
		self.dealer.flip_first_card() #первая из карт, сданных дилеру, переворачивается рубашкой вверх
		for player in self.players:
			print(player)
		print(self.dealer)
		#сдача доп карт игрокам
		for player in self.players:
			self.__additional_cards(player)
		self.dealer.flip_first_card() #первая карта дилера раскрывается
		if not self.still_playing:
			#все игроки перебрали, покажем только "руку" дилера
			print(self.dealer)
			self.dealer.credits += self.kon
			self.kon = 0
		else:
			#сдача доплнительных карт дилеру
			print(self.dealer)
			self.__additional_cards(self.dealer)
			if self.dealer.is_busted():
				#выигрывают все кто остался в игре
				for player in self.still_playing:
					player.win()
					player.credits += self.kon/len(self.still_playing)
			else:
				#сравниваем сумму очков у дилера и игроков оставшихся в игре
				for player in self.still_playing:
					if player.total > self.dealer.total:
						player.win()
						player.credits += self.kon
						self.kon = 0
					elif player.total < self.dealer.total:
						player.lose()
						self.dealer.credits += self.kon
						self.kon = 0
					else:
						player.push()
		#удаление всех карт
		for player in self.players:
			player.clear()
		self.dealer.clear()
		self.kon = 0 #обнуление кона

def main():
	print('\t\tWelcome to Black Jack\n')
	names =[]
	number = games.ask_number('Сколько всего игроков?(1-7)' , low = 1, high =8)
	for i in range(number):
		name = input('Введите имя игрока: ')
		names.append(name)
		print()
	game = BJ_Game(names)
	again = None
	while again != 'n' and len(game.still_playing) != 0:
		game.reload_deck()
		game.play()
		again = games.ask_yes_no("\nХотите сыграть еще? ")

		
	input('.......press enter to exit.......')

main()