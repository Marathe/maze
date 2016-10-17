'''
    goodies.py

    Definitions for some example goodies
'''


import random

from maze import Goody, UP, DOWN, LEFT, RIGHT, STAY, PING, Baddy

from numpy.random import choice

from graphSearch import GridWithWeights, a_star_search, reconstruct_path
 
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
	coords = [100,100]
	previousCoords = []
	turnOn = 200;
	countRound = 0;
	
	grid = GridWithWeights(200, 200)
	
	def __init__(self):
		for i in xrange(100):
			for j in xrange(100):
				self.grid.weights[(i,j)] = 5
		
	
	def updateGrid(self, obstruction):
		notPossibleDirections = filter(lambda direction:  obstruction[direction], [UP, DOWN, LEFT, RIGHT])
		for d in [UP, LEFT, DOWN, RIGHT]:
			coord = tuple(self.whatWouldCoordsBe(d))
			if obstruction[d]:
				self.grid.walls.append(coord)
				if coord in self.grid.weights:
					del self.grid.weights[coord]
			else:
				self.grid.weights[coord] = 0 
		
		
	
	def getRepeatedDirections(self, minNum):
		repeatedDirections = []
		for direction in [LEFT, UP, DOWN, RIGHT]:
			numTimes = self.previousCoords.count(self.whatWouldCoordsBe(direction))
			if numTimes > minNum:
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
		L = [UP, DOWN, LEFT, RIGHT]
		weights = [choices[UP], choices[DOWN], choices[LEFT], choices[RIGHT]]
		
		total = 0
		for w in weights:
			total = total+ w
		c= choice([0, 1, 2, 3], 1, p=[w/total for w in weights])
		return L[c[0]]
   
	def take_turn(self, obstruction, _ping_response):
		self.updateGrid(obstruction)

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
						goodPosition = position
					if isinstance(player, Baddy):
						badDirections = self.makeDirections(obstruction, position)
						
				if False:
					goal = (self.coords[0]+goodPosition.x, self.coords[1] + goodPosition.y)
					came_from, cost_so_far = a_star_search(self.grid, tuple(self.coords), goal)
				
					path = reconstruct_path(came_from, tuple(self.coords), goal)
				else:
					path = None
				if path:
					print self.coords
					print path[2]
					goToCoords = path[2]
					
					if self.coords[0] - goToCoords[0] > 0:
						decision = LEFT
					elif self.coords[0] - goToCoords[0] < 0:
						decision = RIGHT
					elif self.coords[1] - goToCoords[1] > 0:
						decision = DOWN
					else:
						decision = UP
				else:
					notPossibleDirections = filter(lambda direction:  obstruction[direction], [UP, DOWN, LEFT, RIGHT])
					repeatedDirections = self.getRepeatedDirections(2)
					veryRepeatedDirections = self.getRepeatedDirections(10)
					directionWeights = {UP: 2, DOWN: 2, LEFT: 2, RIGHT: 2 }
				
					for d in repeatedDirections:
						directionWeights[d] = directionWeights[d] - .4
					for d in veryRepeatedDirections:
						directionWeights[d] = directionWeights[d] - .4
					for d in goodDirections:
						directionWeights[d] = directionWeights[d] + .8
					for d in badDirections:
						directionWeights[d] = directionWeights[d] - .8
					for d in notPossibleDirections:
						directionWeights[d] = 0
				
					decision = self.weightedChoice(directionWeights)
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
		self.countRound = self.countRound + 1
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
	
	
		
