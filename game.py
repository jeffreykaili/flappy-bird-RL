import pygame
import sys
import os
import neat
from random import*
class Bird:
	def __init__(self):
		self.x = 150
		self.y = 450
		self.grav = 15
		self.alive = True
		self.speed = 0
		self.score = 0 
		self.scoreInc = False
		self.image = pygame.image.load(os.path.join("bird.png")).convert_alpha()
	def jump(self):
		if(self.speed and self.y > 0):
			self.y -= self.speed
			self.speed -= 2
	def ground(self):
		if(self.y > 900-86):
			self.alive = False
			return 0
		return 1
	def rect(self):
		birdRect = self.image.get_rect()
		birdRect.topleft = (self.x, self.y)
		return birdRect
	def collide (self, selfRect, pillarRect):
		if(selfRect.colliderect(pillarRect)): 
			self.alive = False
		elif(selfRect.x > pillarRect.x+280 and (self.scoreInc == False)):
			self.score += 1
			self.scoreInc = True
			return 1

class Tube:
	def __init__(self, top, dist=0, startingx=1000):
		self.top = top
		self.gap = 1000
		self.passed = False
		if(self.top == 1):
			self.image = pygame.image.load(os.path.join("dpipe.png")).convert_alpha()
			self.x = startingx
			self.y = randint(-600, -170)
		else:
			self.image = pygame.image.load(os.path.join("upipe.png")).convert_alpha()
			self.x = startingx
			self.y = dist + self.gap 
	def randY(self):
		self.y = randint(-600, -170) 
	def rect(self):
		pipeRect = self.image.get_rect()
		pipeRect.topleft = (self.x, self.y)
		return pipeRect
	def move(self, dist=0):
		if(self.x > -282-100):
			self.x -= 18 
		else:
			self.x = 1600 
			if(dist):
				self.y = dist + self.gap 
			else:
				self.randY() 
			return True
global generation 
generation = 1

def game(network, config):
	os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d"%(100,100)
	pygame.init()
	screen = pygame.display.set_mode((1600, 900))
	FPS = 60
	gameOver = False

	birdList = []
	birdTrueIndex = []
	networks = []
	genetic = []
	currentBird = 0
	index = 0
	for x, nn in network:
		nn.fitness = 0
		birdList.append(Bird())
		networks.append(neat.nn.FeedForwardNetwork.create(nn,config))
		genetic.append(nn)
		birdTrueIndex.append(index)
		index += 1 

	background = pygame.image.load(os.path.join("background.png")).convert_alpha()
	uppipe = Tube(1)
	downpipe = Tube(0, uppipe.y)
	uppipe2 = Tube(1,0,1650)
	downpipe2 = Tube(0, uppipe2.y, uppipe2.x)
	uppipe3 = Tube(1,0,2300)
	downpipe3 = Tube(0, uppipe3.y, uppipe3.x)
	pipes = [(uppipe, downpipe), (uppipe2, downpipe2), (uppipe3, downpipe3)] 
	font = pygame.font.Font('visitor1.ttf', 72) 
	genFont = pygame.font.Font('visitor1.ttf', 54) 

	while not gameOver:
		global generation
		pygame.time.Clock().tick(FPS)

		frontPipe = None
		if(birdList[0].score%3==0):frontPipe=0
		elif(birdList[0].score%3==1):frontPipe=1
		else:frontPipe=2
		secondPipe = (frontPipe+1)%3

		for index, bird in enumerate(birdList):
			decision = networks[index].activate((bird.y, abs(bird.y-(pipes[frontPipe][0].y+700)), abs(bird.y-pipes[frontPipe][1].y), abs(bird.y-(pipes[secondPipe][0].y+700)), abs(bird.y-pipes[secondPipe][1].y)))[0]
			if(decision > 0.5):
				bird.speed = 35
		for event in pygame.event.get(): 
			if(event.type == pygame.QUIT):
				sys.exit() 

		for bird in birdList:
			bird.y += bird.grav
		for pipe in pipes: 
			reset=pipe[0].move() 
			pipe[1].move(pipe[0].y) 
			if(reset == True):
				for bird in birdList:
					bird.scoreInc = 0 
		for index, bird in enumerate(birdList):
			bird.jump()
			ground = bird.ground()
			if not(ground):
				genetic[index].fitness -= 2
				del birdList[index]
				del genetic[index]
				del networks[index]
				del birdTrueIndex[index]
		for pipe in pipes:
			index = 0 
			for bird in birdList:
				first=bird.collide(bird.rect(), pipe[0].rect())
				second=bird.collide(bird.rect(), pipe[1].rect())
				if(bird.alive == False): 
					genetic[index].fitness -= 3
					del birdList[index]
					del genetic[index]
					del networks[index]
					del birdTrueIndex[index]
				elif(first == 1 or second == 1): 
					genetic[index].fitness += 5
				else:
					genetic[index].fitness += 0.05
				index += 1 

		if(len(birdList)==0):
			gameOver=True
			generation += 1 
			break
		screen.fill((255,255,255)) 
		screen.blit(background,(0,0))
		for pipe in pipes:
			screen.blit(pipe[0].image, (pipe[0].x, pipe[0].y))
			screen.blit(pipe[1].image, (pipe[1].x, pipe[1].y))
		#for bird in birdList:
			#screen.blit(bird.image, (bird.x,bird.y))
		screen.blit(birdList[currentBird].image, (birdList[currentBird].x, birdList[currentBird].y)) 
		screen.blit(font.render(str(birdList[currentBird].score), False, (255,255,255)), (740, 100))
		screen.blit(genFont.render("GENERATION: "+str(generation), False, (255,255,255)), (20, 10))
		screen.blit(genFont.render("WATCHING BIRD: "+str(birdTrueIndex[currentBird]), False, (255,255,255)), (1060, 10))
		print(birdList[currentBird].collide(bird.rect(), pipe[1].rect()), birdList[currentBird].collide(bird.rect(), pipe[0].rect()))
		pygame.display.update()


def main(cPath):
	config=neat.config.Config(neat.DefaultGenome,neat.DefaultReproduction,neat.DefaultSpeciesSet,neat.DefaultStagnation,cPath)
	population=neat.Population(config)
	population.add_reporter(neat.StdOutReporter(1))
	population.add_reporter(neat.StatisticsReporter())
	best=population.run(game,100)
if(__name__=="__main__"):
	main(os.path.join(os.path.dirname(__file__),"config.txt"))