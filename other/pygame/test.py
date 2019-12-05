import pygame
import sys
import random

black = (0, 0, 0)
white = (255, 255, 255)
blue = (0, 0, 255)
red = (255, 0, 0)
yellow = (255, 255, 0)
green = (0, 255, 0)
purple = (0, 255, 255)

x = random.randint(20, 380)
y = 0
w = 50 # initial block width
h = 100 # initial block height
all_blocks = []
score = 0

# check collision of block with all existing blocks (+ floor)
def collided(block, all_blocks):
	for i in range(len(all_blocks)):
		if block.colliderect(all_blocks[i]):
			return True
	return False

clock = pygame.time.Clock()

pygame.init()

screen = pygame.display.set_mode([400, 700])

# use a white background for the screen
screen.fill(white)
pygame.display.update()

floor = pygame.draw.rect(screen, black, [0, 700, 700, 1], 0)
all_blocks.insert(0, floor)

# starting block color
color = red
gameover = False

while gameover == False:
	
	# erase the previous block
	pygame.draw.rect(screen, white, [x, y, w, h], 0)
	
	# event loop - check for key left/right events, and quit
	for event in pygame.event.get():
		
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_LEFT:
				x = x - 20
			if event.key == pygame.K_RIGHT:
				x = x + 20
			if event.key == pygame.K_SPACE: 
			   
				# cover up the previous rectangle
				pygame.draw.rect(screen, white, [x, y, w, h], 0)
				
				# swap w and h dimensions
				temp = h
				h = w
				w = temp
	
	# drop the block further				
	    y = y + 3
	
	# ensure that we don't go out of bounds
        if x < 0:
            x = 0 
            if x + w > 400:
                x = 400 - w
	
	# draw the new block (falling down screen)
	block = pygame.draw.rect(screen, color, [x, y, w, h], 0)
	
	# if collision with any existing block, reset to top of screen
	if collided(block, all_blocks):
	
		# if the y position of block is <= 10, then game over!!
		if y < 10:
			gameover = True

		# random block position
		y = 0
		x = random.randint(20, 380)
	
		# new random block size
		w = random.randint(50, 100)
		h = random.randint(50, 100)
	
		# add the block to our collection of "fallen" blocks
		all_blocks.insert(0, block)
	
		randomnum = random.randint(0, 4)
	
		if randomnum == 0:
			color = blue
		if randomnum == 1:
			color = red
		if randomnum == 2:
			color = green
		if randomnum == 3:
			color = purple
		if randomnum == 4:
			color = black
		
		score = score + 1
		print ("score = " + str(score))

	# refresh the display
	pygame.display.update()
	
	# display "refresh" speed = 15 frames per second
	clock.tick(100)

print ("The Game is OVER!!!")