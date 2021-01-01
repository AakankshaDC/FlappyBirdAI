'''
Objects used in the game:
1. Pipes
2. Bird itself
3. The ground
'''
# run is command + B
import pygame
import neat
import time
import os
import random
pygame.font.init() 

WINDOW_HEIGHT = 800
WINDOW_WIDTH = 500

# importing all objects
BIRD_IMAGES = [pygame.transform.scale2x(pygame.image.load(os.path.join("images","bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("images","bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("images","bird3.png")))] 
PIPE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("images","pipe.png")))
BASE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("images","base.png")))
BG_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("images","bg.png")))

# fonts to draw the score
STAT_FONT = pygame.font.SysFont("comicsans", 50)

class Bird:
	IMAGES = BIRD_IMAGES
	MAX_ROTATION = 25 # how much the bird will tilt 
	ROTATION_VELOCITY = 20 
	ANIMATION_TIME = 5 # flow fast is our bird going to flap its wing

	def __init__(self, x, y):
		self.x = x # starting x position of our bird
		self.y = y # starting y position of our bird
		self.tilt = 0 # initial tilt of bird
		self.tick_count = 0 # to determine physics of our bird
		self.velocity = 0 # init velo.
		self.height = self.y 
		self.image_count = 0 # which bird we are using
		self.img = self.IMAGES[0]

	def jump(self):
		'''
		bird to flap up and jump
		'''
		self.velocity = -10.5 # top is negative velocity, down is positive velocity
		self.tick_count = 0 # when we last jumped
		self.height = self.y # where bird originally started moving from

	def move(self):
		'''
		calculation on how much they need to move
		'''
		self.tick_count +=1 # a fram went by since the last jump
		dispacement = self.velocity * self.tick_count + 1.5 * self.tick_count**2 # how many pixels we are moving up or down
		# -10.5 + 1.5 = -9 moving 9 pixels upwars

		if dispacement >= 16: # terminal velocity
			dispacement = 16

		if dispacement < 0: # fine tuned upward movement
			dispacement -= 2
		self.y = self.y + dispacement

		# tiling the bird
		if dispacement < 0 or self.y < self.height + 50: # tilt only if bird is down than org pos
			if self.tilt < self.MAX_ROTATION:
				self.tilt = self.MAX_ROTATION # to avoid rotating more than needed
		else:
			if self.tilt > -90:
				self.tilt = -self.ROTATION_VELOCITY # nose diving into thee ground


	def draw(self, window):
		'''
		draw bird in window
		'''
		self.image_count += 1 # count of our interation, decide which image we will use

		if self.image_count < self.ANIMATION_TIME:
			self.img = self.IMAGES[0] # display the first bird image
		elif self.image_count < self.ANIMATION_TIME * 2:
			self.img = self.IMAGES[1] # display the second bird image
		elif self.image_count < self.ANIMATION_TIME * 3:
			self.img = self.IMAGES[2]
		elif self.image_count < self.ANIMATION_TIME * 4:
			self.img = self.IMAGES[1]
		elif self.image_count == self.ANIMATION_TIME * 4 + 1:
			self.img = self.IMAGES[0]
			self.image_count = 0 # reset

		# no falpping if bird is on 90 degree
		if self.tilt <= -80:
			self.img = self.IMAGES[1]
			self.image_count = self.ANIMATION_TIME*2

		# rotate the bird around its centre
		rotated_image = pygame.transform.rotate(self.img, self.tilt) # rotates along top left corner
		new_rect = rotated_image.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center) # fixing that here

		window.blit(rotated_image, new_rect.topleft)


	def get_mask(self):
		'''
		deal with collision 
		'''
		return pygame.mask.from_surface(self.img)

class Pipe:
	GAP = 200 # space in between our 2 pipes
	PIPE_VELOCITY = 5

	def __init__(self, x):
		# height will be random always thus no y
		self.x = x
		self.height = 0

		self.top = 0 # keeping the track of where the top pipe is going to be drawn
		self.bottom = 0 # keeping the track of where the bottom pipe is going to be drawn

		self.PIPE_TOP = pygame.transform.flip(PIPE_IMAGE, False, True) # get a pipe upside down and we have a pipe that faces upar by default
		self.PIPE_BOTTOM = PIPE_IMAGE

		self.passed = False # has the bird fly passed the pipe already? --> True
		self.set_height()

	def set_height(self):
		'''
		define where the top and bottom pipes are and how tall they are, and the gap
		'''
		self.height = random.randrange(50,450)
		self.top = self.height - self.PIPE_TOP.get_height()
		self.bottom = self.height + self.GAP

	def move(self):
		'''
		change the x position based on the speed pipe should move each frame
		'''
		self.x -= self.PIPE_VELOCITY

	def draw(self, window):
		'''
		draw both top and bottom pipes
		'''
		window.blit(self.PIPE_TOP,(self.x, self.top)) # draw top pipe
		window.blit(self.PIPE_BOTTOM,(self.x, self.bottom)) # draw bottom pipe

	def collide(self, bird):
		'''
		we will make a note of all pixels inside the bird and for each pipe and check for collision
		'''
		bird_mask = bird.get_mask()

		# for top and bottom pipe
		top_mask = pygame.mask.from_surface(self.PIPE_TOP)
		bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

		# offset -- how far are these masks away from each other
		# top_offset = (self.x - bird.x, self.top - round(bird.y)) # offset of the bird from top mask
		# bottom_offset = (self.x - bird.x, self.bottom - round(bird.y)) # offset of the bird from bottom mask
		top_offset = (self.x - bird.x, int(self.top - round(bird.y)))
		bottom_offset = (self.x - bird.x, int(self.bottom - round(bird.y)))

		bottom_point_of_collision = bird_mask.overlap(bottom_mask, bottom_offset)
		top_point_of_collision = bird_mask.overlap(top_mask, top_offset)

		if top_point_of_collision or bottom_point_of_collision:
			# collision occured
			return True

		return False

class Base:
	BASE_VELOCITY = 5 # same as pipe veelocity
	BASE_WIDTH = BASE_IMAGE.get_width() # how wide our base image is
	IMG = BASE_IMAGE

	def __init__(self, y):
		self.y = y
		self.x1 = 0
		self.x2 = self.BASE_WIDTH

	def move(self):
		self.x1 -= self.BASE_VELOCITY
		self.x2 -= self.BASE_VELOCITY

		if self.x1 + self.BASE_WIDTH < 0:
			self.x1 = self.x2 + self.BASE_WIDTH # put 1st image behind

		if self.x2 + self.BASE_WIDTH < 0:
			self.x2 = self.x1 + self.BASE_WIDTH # put 2nd image behind

	def draw(self, window):
		window.blit(self.IMG, (self.x1, self.y))
		window.blit(self.IMG, (self.x2 , self.y))

def draw_window(window, birdObjects, pipes, base, score):
	# draw the background
	window.blit(BG_IMAGE, (0,0)) # draw on top left
	for pipe in pipes:
		pipe.draw(window)

	# reder the font
	text = STAT_FONT.render("Score: "+ str(score), 1, (255,255,255))
	window.blit(text, (WINDOW_WIDTH - 10 - text.get_width(), 10))

	base.draw(window)
	for bird in birdObjects:
		bird.draw(window)

	pygame.display.update()

def main(genomes, config):
	birdObjects = [] # upadte this to deal with multiple birds
	neural_nets = [] # neeural network for each bird
	genome_list = [] # genome list to maintain fitness info for each bird

	for _ , g in genomes:
		net = neat.nn.FeedForwardNetwork.create(g, config)
		neural_nets.append(net)
		birdObjects.append(Bird(230,350))

		g.fitness = 0 # set initial fitness of birds to be zero 
		genome_list.append(g)

	
	
	base = Base(730) # where to have the base photo should be
	pipes = [Pipe(600)]
	window =pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
	clock = pygame.time.Clock()

	score = 0

	run = True
	while run:
		clock.tick(30)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()
				quit()

		# move the brids based on the neural network
		pipe_ind = 0
		if len(birdObjects) > 0:
			if len(pipes) > 1 and birdObjects[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width(): # if pipee 0 has passed
				pipe_ind = 1
		else:
			# quit running the game
			run = False
			break

		for x, bird in enumerate(birdObjects):
			bird.move()
			# give reward for coming this far
			genome_list[x].fitness += 0.1

			# activate our neural network
			output = neural_nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

			if output[0] > 0.5:
				bird.jump()

		# birdObject.move() # to make our bird move but will immediately fall, thus a tick rate
		add_pipe = False
		rem = []
		for pipe in pipes:
			for x, bird in enumerate(birdObjects):
				# collision detection 
				if pipe.collide(bird):
					# remove birds that collide and stagnate its fitness
					genome_list[x].fitness -= 1
					# remove all
					birdObjects.pop(x)
					neural_nets.pop(x)
					genome_list.pop(x)

				if not pipe.passed and pipe.x < bird.x: # as soon as the pipe is passed generate a new one
					pipe.passed = True
					add_pipe =True

			if pipe.x + pipe.PIPE_TOP.get_width() < 0: # if pipe is completely off the screen, remove that pipe
				rem.append(pipe)

			pipe.move()

		# if a bird made it through a pipe
		if add_pipe:
			score += 1
			# also add some fitness to the ones that passed the pipe 
			for g in genome_list:
				g.fitness += 5
			# create a new pipe
			pipes.append(Pipe(600))

		for r in rem: # remove all the pipes that are off the screen
			pipes.remove(r)

		for x, bird in enumerate(birdObjects):
			# check if the bird has hit the ground, this part is essential because we are going to use a genetic algorithm to identify which instance was a failure anyway
			if bird.y + bird.img.get_height() >= 730 or bird.y < 0: # we hit the floor or birds flew on the top of the screen
				birdObjects.pop(x)
				neural_nets.pop(x)
				genome_list.pop(x)

		base.move()
		draw_window(window, birdObjects, pipes, base, score)

	# pygame.quit()
	# quit()


def run(config_file):
	# load file here, then run the NEAT Algorithm
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)
	
	# use the config file here
	population = neat.Population(config)
	population.add_reporter(neat.StdOutReporter(True)) # stats of each generation to bee displayed in the terminal
	stats = neat.StatisticsReporter()
	population.add_reporter(stats)

	winner = population.run(main, 50) # run fitness funtion for 50 generations, call main() 50 times and pass the geenome and config file

if __name__ == "__main__":
	# get path to config file
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, "config-feedforward.txt")
	run(config_path)
