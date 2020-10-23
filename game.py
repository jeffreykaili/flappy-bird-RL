import pygame
import sys
import os
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

def game():
	pygame.init()
	screen = pygame.display.set_mode((1600, 900))
	FPS = 60
	gameOver = False
	bird = Bird() 
	background = pygame.image.load(os.path.join("background.png")).convert_alpha()
	uppipe = Tube(1)
	downpipe = Tube(0, uppipe.y)
	uppipe2 = Tube(1,0,1650)
	downpipe2 = Tube(0, uppipe2.y, uppipe2.x)
	uppipe3 = Tube(1,0,2300)
	downpipe3 = Tube(0, uppipe3.y, uppipe3.x)
	pipes = [(uppipe, downpipe), (uppipe2, downpipe2), (uppipe3, downpipe3)] 
	font = pygame.font.Font('visitor1.ttf', 72) 
	while not gameOver:
		pygame.time.Clock().tick(FPS) 
		if not (bird.alive):
			gameOver = True
		for event in pygame.event.get(): 
			if(event.type == pygame.QUIT):
				sys.exit() 
			if(event.type == pygame.KEYDOWN):
				if(event.key == pygame.K_SPACE):
					bird.speed = 35
		bird.y += bird.grav
		for pipe in pipes: 
			reset=pipe[0].move() 
			pipe[1].move(pipe[0].y) 
			if(reset == True):
				bird.scoreInc = 0 
		bird.jump()
		bird.ground()
		for pipe in pipes:
			bird.collide(bird.rect(), pipe[0].rect())
			bird.collide(bird.rect(), pipe[1].rect())
		screen.fill((255,255,255)) 
		screen.blit(background,(0,0))
		for pipe in pipes:
			screen.blit(pipe[0].image, (pipe[0].x, pipe[0].y))
			screen.blit(pipe[1].image, (pipe[1].x, pipe[1].y))
		screen.blit(bird.image, (bird.x, bird.y)) 
		screen.blit(font.render(str(bird.score), False, (255,255,255)), (740, 100))
		pygame.display.update()
game()