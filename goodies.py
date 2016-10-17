'''
    goodies.py

    Definitions for some example goodies
'''


import random

from maze import Goody, UP, DOWN, LEFT, RIGHT, STAY, PING, Baddy

from numpy.random import choice

class StaticGoody(Goody):
    ''' A static goody - does not move from its initial position '''

    def take_turn(self, _obstruction, _ping_response):
        ''' Stay where we are '''
        return STAY

class RandomGoody(Goody):
    ''' A random-walking goody '''

    def take_turn(self, obstruction, _ping_response):
        ''' Ignore any ping information, just choose a random direction to walk in, or ping '''
        possibilities = filter(lambda direction: not obstruction[direction], [UP, DOWN, LEFT, RIGHT]) + [PING]
        return random.choice(possibilities)


class MoveTowards(Goody):
	lastPing = None
	turnsSincePing = 0
	coords = [0,0]
	previousCoords = []
	


	
	def getRepeatedDirections(self):
		repeatedDirections = []
		for direction in [LEFT, UP, DOWN, RIGHT]:
			numTimes = self.previousCoords.count(self.whatWouldCoordsBe(direction))
			if numTimes > 2:
				repeatedDirections.append(direction)
		return repeatedDirections
		



	def whatWouldCoordsBe(self, choice):
		newCoords = self.coords
		if choice == UP:
			newCoords[1] = self.coords[1] + 1
		elif choice == DOWN:
			newCoords[1] = self.coords[1] - 1
		elif choice == LEFT:
			newCoords[0] = self.coords[0] - 1
		elif choice == RIGHT:
			newCoords[0] = self.coords[0] + 1
		return newCoords
		
	def updateCoords(self, choice):
		self.coords = self.whatWouldCoordsBe(choice)
	
	def makeDirections(self, obstruction, position):
		directions = []
		if position.x > 0:
			directions.append(RIGHT)
		elif position.x < 0 :
			directions.append(LEFT)
		if position.y > 0:
			directions.append(UP)
		elif position.y < 0 :
			directions.append(DOWN)						
		return filter(lambda direction: not obstruction[direction], directions)
	
	def weightedChoice(self, choices):
		
		print choices
		total = 0
		for c,w in choices.iteritems():
			total = total+ w
		print [w/total for c,w in choices.iteritems()]
		print choice(choices.keys(), 1, [w/total for c,w in choices.iteritems()])[0]
		return choice(choices.keys(), 1, [w/total for c,w in choices.iteritems()])[0]
   
	def take_turn(self, obstruction, _ping_response):
		decision = None
		if _ping_response is not None:
			self.lastPing = _ping_response
			self.turnsSincePing = 0;
		
		if self.lastPing is None:
			decision =  PING
		else:
			if self.turnsSincePing==10:
				self.turnsSincePing = 0
				decision =  PING
			else:
				self.turnsSincePing = self.turnsSincePing + 1
				for player, position in self.lastPing.iteritems():
					if isinstance(player,Goody):
						goodDirections = self.makeDirections(obstruction, position)
					if isinstance(player, Baddy):
						badDirections = self.makeDirections(obstruction, position)
				notPossibleDirections = filter(lambda direction:  obstruction[direction], [UP, DOWN, LEFT, RIGHT])
				repeatedDirections = self.getRepeatedDirections()
				
				directionWeights = {UP: 2, DOWN: 2, LEFT: 2, RIGHT: 2 }
				
				for d in repeatedDirections:
					directionWeights[d] = directionWeights[d] - .4
				for d in goodDirections:
					directionWeights[d] = directionWeights[d] + .8
				for d in badDirections:
					directionWeights[d] = directionWeights[d] - .8
				for d in notPossibleDirections:
					directionWeights[d] = 0
				
				decision = self.weightedChoice(directionWeights)
				print decision
				# bestDirections = [item for item in goodDirections if item not in badDirections]
				# print bestDirections
				# if bestDirections:
					# decision = random.choice(bestDirections)
				# elif goodDirections:
					# decision = random.choice(goodDirections)
				# else:
					# possibleDirections = filter(lambda direction: not obstruction[direction], [UP, DOWN, LEFT, RIGHT])
					# secondBestDirections = [item for item in possibleDirections if item not in badDirections]
					# if secondBestDirections:
						# decision = random.choice(secondBestDirections)
					# else:
						# decision = random.choice(possibleDirections)

		self.updateCoords(decision)
		self.previousCoords.append(self.coords)
		return decision
		



class MemoryGoody(Goody):
	map = [[None for i in xrange(51)] for j in xrange(51)]
	coords = [0,0]
	def __init__(self): 
		# set own coordinates to unobstructed
		self.map[self.coords[0]][self.coords[1]] = 0
	
	def updateCoords(self, choice):
		if choice == UP:
			self.coords[1] = self.coords[1] + 1
		elif choice == DOWN:
			self.coords[1] = self.coords[1] - 1
		elif choice == LEFT:
			self.coords[0] = self.coords[0] - 1
		elif choice == RIGHT:
			self.coords[0] = self.coords[0] + 1

	def take_turn(self, obstruction, _ping_response):
		#''' Ignore any ping information, just choose a random direction to walk in, or ping '''
        #possibilities = filter(lambda direction: not obstruction[direction], [UP, DOWN, LEFT, RIGHT]) + [PING]
		#choice = random.choice(possibilities)
		#updateCoords(self, choice)
		return UP
		
	
		
if __name__ == "__main__":
	g = MemoryGoody();
	print g.coords
	g.updateCoords(g,UP)
	print g.coords
	
	
		
