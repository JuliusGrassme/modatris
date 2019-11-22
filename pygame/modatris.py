# Control keys:
# Down - Drop stone faster
# Left/Right - Move stone
# Up - Rotate Stone clockwise
# Escape - Quit game
# P - Pause game

from random import randrange as rand
import pygame, sys

# The configuration
config = {
	'cell_size':	20,
	'cols':		16,
	'rows':		32,
	'delay':	750,
	'maxfps':	30
}

colors = [
(0,   0,   0  ),
(189, 119, 223),
(119, 154, 223),
(0,   0,   255),
(255, 120, 0  ),
(255, 255, 0  ),
(180, 0,   255),
(0,   220, 220)
]

# Define the shapes of the single parts

advanced = [
	[[2, 0, 0],
	 [2, 2, 0],
	 [2, 2, 2]],

	[[0, 0, 2],
	 [0, 2, 0],
	 [2, 0, 0]],

	[[2, 0, 2],
	 [0, 2, 0]],

	[[0, 2, 0],
	 [2, 2, 2],
	 [0, 2, 0]],

	[[0, 2, 2],
	 [2, 2, 0]],

	[[2, 2, 0],
	 [0, 2, 2]],

	[[2, 0, 2],
	 [0, 2, 0],
	 [2, 0, 2]],
	
	[[2, 2, 2],
	 [2, 2, 2],
	 [2, 2, 2]],

	[[2, 0, 2],
	 [0, 0, 0],
	 [2, 0, 2]],

	[[2, 0, 0, 0],
	 [2, 2, 0, 0],
	 [2, 2, 2, 0],
	 [2, 2, 2, 2]]]

normal = [
	[[1, 1, 1],
	 [0, 1, 0]],

	[[0, 1, 1],
	 [1, 1, 0]],
 
	[[1, 1, 0],
	 [0, 1, 1]],
 
	[[1, 0, 0],
	 [1, 1, 1]],
 
	[[0, 0, 1],
	 [1, 1, 1]],

	[[1, 1, 1, 1]],
 
	[[1, 1],
	 [1, 1]],
 
	[[1, 1, 0],
	 [1, 1, 1]],
 
	[[1, 1]],

	[[1]]]

level1 = [
	[[1, 1, 1],
	 [0, 1, 0]],

	[[0, 1, 1],
	 [1, 1, 0]],
 
	[[1, 1, 0],
	 [0, 1, 1]],
 
	[[1, 0, 0],
	 [1, 1, 1]],
 
	[[0, 0, 1],
	 [1, 1, 1]],

	[[1, 1, 1, 1]],
 
	[[1, 1],
	 [1, 1]],
 
	[[1, 1, 0],
	 [1, 1, 1]],
 
	[[1, 1]],

	[[2, 0, 0, 0],
	 [2, 2, 0, 0],
	 [2, 2, 2, 0],
	 [2, 2, 2, 2]]]

level2 = [
	[[1, 1, 1],
	 [0, 1, 0]],

	[[0, 1, 1],
	 [1, 1, 0]],
 
	[[1, 1, 0],
	 [0, 1, 1]],
 
	[[1, 0, 0],
	 [1, 1, 1]],
 
	[[0, 0, 1],
	 [1, 1, 1]],

	[[1, 1, 1, 1]],
 
	[[1, 1],
	 [1, 1]],
 
	[[1, 1, 0],
	 [1, 1, 1]],

	[[2, 0, 2],
	 [0, 0, 0],
	 [2, 0, 2]],

	[[2, 0, 0, 0],
	 [2, 2, 0, 0],
	 [2, 2, 2, 0],
	 [2, 2, 2, 2]]]

level3 =  [
	[[1, 1, 1],
	 [0, 1, 0]],

	[[0, 1, 1],
	 [1, 1, 0]],
 
	[[1, 1, 0],
	 [0, 1, 1]],
 
	[[1, 0, 0],
	 [1, 1, 1]],
 
	[[0, 0, 1],
	 [1, 1, 1]],

	[[1, 1, 1, 1]],
 
	[[1, 1],
	 [1, 1]],

	[[2, 2, 2],
	 [2, 2, 2],
	 [2, 2, 2]],

	[[2, 0, 2],
	 [0, 0, 0],
	 [2, 0, 2]],

	[[2, 0, 0, 0],
	 [2, 2, 0, 0],
	 [2, 2, 2, 0],
	 [2, 2, 2, 2]]]

level4 =  [
	[[1, 1, 1],
	 [0, 1, 0]],

	[[0, 1, 1],
	 [1, 1, 0]],
 
	[[1, 1, 0],
	 [0, 1, 1]],
 
	[[1, 0, 0],
	 [1, 1, 1]],
 
	[[0, 0, 1],
	 [1, 1, 1]],

	[[1, 1, 1, 1]],

	[[2, 0, 2],
	 [0, 2, 0],
	 [2, 0, 2]],
	
	[[2, 2, 2],
	 [2, 2, 2],
	 [2, 2, 2]],

	[[2, 0, 2],
	 [0, 0, 0],
	 [2, 0, 2]],

	[[2, 0, 0, 0],
	 [2, 2, 0, 0],
	 [2, 2, 2, 0],
	 [2, 2, 2, 2]]]

level5 =  [
	[[1, 1, 1],
	 [0, 1, 0]],

	[[0, 1, 1],
	 [1, 1, 0]],
 
	[[1, 1, 0],
	 [0, 1, 1]],
 
	[[1, 0, 0],
	 [1, 1, 1]],
 
	[[0, 0, 1],
	 [1, 1, 1]],

	[[2, 2, 0],
	 [0, 2, 2]],

	[[2, 0, 2],
	 [0, 2, 0],
	 [2, 0, 2]],
	
	[[2, 2, 2],
	 [2, 2, 2],
	 [2, 2, 2]],

	[[2, 0, 2],
	 [0, 0, 0],
	 [2, 0, 2]],

	[[2, 0, 0, 0],
	 [2, 2, 0, 0],
	 [2, 2, 2, 0],
	 [2, 2, 2, 2]]]

level6 =  [
	[[1, 1, 1],
	 [0, 1, 0]],

	[[0, 1, 1],
	 [1, 1, 0]],
 
	[[1, 1, 0],
	 [0, 1, 1]],
 
	[[1, 0, 0],
	 [1, 1, 1]],

	[[0, 2, 2],
	 [2, 2, 0]],

	[[2, 2, 0],
	 [0, 2, 2]],

	[[2, 0, 2],
	 [0, 2, 0],
	 [2, 0, 2]],
	
	[[2, 2, 2],
	 [2, 2, 2],
	 [2, 2, 2]],

	[[2, 0, 2],
	 [0, 0, 0],
	 [2, 0, 2]],

	[[2, 0, 0, 0],
	 [2, 2, 0, 0],
	 [2, 2, 2, 0],
	 [2, 2, 2, 2]]]

level7 = [
	[[1, 1, 1],
	 [0, 1, 0]],

	[[0, 1, 1],
	 [1, 1, 0]],
 
	[[1, 1, 0],
	 [0, 1, 1]],

	[[0, 2, 0],
	 [2, 2, 2],
	 [0, 2, 0]],

	[[0, 2, 2],
	 [2, 2, 0]],

	[[2, 2, 0],
	 [0, 2, 2]],

	[[2, 0, 2],
	 [0, 2, 0],
	 [2, 0, 2]],
	
	[[2, 2, 2],
	 [2, 2, 2],
	 [2, 2, 2]],

	[[2, 0, 2],
	 [0, 0, 0],
	 [2, 0, 2]],

	[[2, 0, 0, 0],
	 [2, 2, 0, 0],
	 [2, 2, 2, 0],
	 [2, 2, 2, 2]]]

level8 =[
	[[1, 1, 1],
	 [0, 1, 0]],

	[[0, 1, 1],
	 [1, 1, 0]],

	[[2, 0, 2],
	 [0, 2, 0]],

	[[0, 2, 0],
	 [2, 2, 2],
	 [0, 2, 0]],

	[[0, 2, 2],
	 [2, 2, 0]],

	[[2, 2, 0],
	 [0, 2, 2]],

	[[2, 0, 2],
	 [0, 2, 0],
	 [2, 0, 2]],
	
	[[2, 2, 2],
	 [2, 2, 2],
	 [2, 2, 2]],

	[[2, 0, 2],
	 [0, 0, 0],
	 [2, 0, 2]],

	[[2, 0, 0, 0],
	 [2, 2, 0, 0],
	 [2, 2, 2, 0],
	 [2, 2, 2, 2]]]

level9 = [
	[[1, 1, 1],
	 [0, 1, 0]],

	[[0, 0, 2],
	 [0, 2, 0],
	 [2, 0, 0]],

	[[2, 0, 2],
	 [0, 2, 0]],

	[[0, 2, 0],
	 [2, 2, 2],
	 [0, 2, 0]],

	[[0, 2, 2],
	 [2, 2, 0]],

	[[2, 2, 0],
	 [0, 2, 2]],

	[[2, 0, 2],
	 [0, 2, 0],
	 [2, 0, 2]],
	
	[[2, 2, 2],
	 [2, 2, 2],
	 [2, 2, 2]],

	[[2, 0, 2],
	 [0, 0, 0],
	 [2, 0, 2]],

	[[2, 0, 0, 0],
	 [2, 2, 0, 0],
	 [2, 2, 2, 0],
	 [2, 2, 2, 2]]]

measurement = rand(0,10) # measurements from sensor - plug in own data

print(measurement)

def rotate_clockwise(shape):
	return [[shape[y][x] for y in range(len(shape))]
		for x in range(len(shape[0]) - 1, -1, -1)]

def check_collision(board, shape, offset):
	off_x, off_y = offset
	for cy, row in enumerate(shape):
		for cx, cell in enumerate(row):
			try:
				if cell and board[ cy + off_y ][ cx + off_x ]:
					return True
			except IndexError:
				return True
	return False

def remove_row(board, row):
	del board[row]
	return [[0 for i in range(config['cols'])]] + board
	
def join_matrixes(mat1, mat2, mat2_off):
	off_x, off_y = mat2_off
	for cy, row in enumerate(mat2):
		for cx, val in enumerate(row):
			mat1[cy+off_y-1	][cx+off_x] += val
	return mat1

def new_board():
	board = [[0 for x in range(config['cols'])] for y in range(config['rows']) ]
	board += [[ 1 for x in range(config['cols'])]]
	return board

class TetrisApp(object):
	def __init__(self):
		pygame.init()
		pygame.key.set_repeat(250,25)
		self.width = config['cell_size']*config['cols']
		self.height = config['cell_size']*config['rows']
		self.screen = pygame.display.set_mode((self.width, self.height))
		pygame.event.set_blocked(pygame.MOUSEMOTION)
		self.init_game()
	
	def new_stone(self):
		# make sure to update the if statements according to 
		# the readings from the sensors
		
		self.stone_y = 0
		if measurement == 0:			
			self.stone = normal[rand(len(normal))]
			self.stone_y += 1
		elif measurement == 1:
			self.stone = level1[rand(len(level1))]
			self.stone_y += 2
		elif measurement == 2:
			self.stone = level2[rand(len(level2))]
			self.stone_y += 3
		elif measurement == 3:
			self.stone = level3[rand(len(level3))]
			self.stone_y += 4
		elif measurement == 4:
			self.stone = level4[rand(len(level4))]
			self.stone_y += 5
		elif measurement == 5:
			self.stone == level5[rand(len(level5))]
			self.stone_y += 6
		elif measurement == 6:
			self.stone = level6[rand(len(level6))]
			self.stone_y += 7
		elif measurement == 7:
			self.stone = level7[rand(len(level7))]
			self.stone_y += 8
		elif measurement == 8:
			self.stone = level8[rand(len(level8))]
			self.stone_y += 9
		elif measurement == 9:
			self.stone = level9[rand(len(level9))]
			self.stone_y += 10
		else:
			print ("Please make sure sensors are configured properly!")

		self.stone_x = int(config['cols'] / 2 - len(self.stone[0])/2)
		
		
		if check_collision(self.board, self.stone, (self.stone_x, self.stone_y)):
			self.gameover = True
	
	def init_game(self):
		self.board = new_board()
		self.new_stone()
	
	def center_msg(self, msg):
		for i, line in enumerate(msg.splitlines()):
			msg_image =  pygame.font.Font(pygame.font.get_default_font(), 12).render(line, False, (255,255,255), (0,0,0))
			msgim_center_x, msgim_center_y = msg_image.get_size()
			msgim_center_x //= 2
			msgim_center_y //= 2
			self.screen.blit(msg_image, (self.width // 2-msgim_center_x, self.height // 2-msgim_center_y+i*22))
	
	def draw_matrix(self, matrix, offset):
		off_x, off_y  = offset
		for y, row in enumerate(matrix):
			for x, val in enumerate(row):
				if val:
					pygame.draw.rect(self.screen, colors[val], pygame.Rect((off_x+x) * config['cell_size'], (off_y+y) * config['cell_size'],  config['cell_size'], config['cell_size']),0)
	
	def move(self, delta_x):
		if not self.gameover and not self.paused:
			new_x = self.stone_x + delta_x
			if new_x < 0:
				new_x = 0
			if new_x > config['cols'] - len(self.stone[0]):
				new_x = config['cols'] - len(self.stone[0])
			if not check_collision(self.board, self.stone, (new_x, self.stone_y)):
				self.stone_x = new_x
	def quit(self):
		self.center_msg("Exiting...")
		pygame.display.update()
		sys.exit()
	
	def drop(self):
		if not self.gameover and not self.paused:
			self.stone_y += 1
			if check_collision(self.board, self.stone, (self.stone_x, self.stone_y)):
				self.board = join_matrixes(self.board, self.stone, (self.stone_x, self.stone_y))
				self.new_stone()
				while True:
					for i, row in enumerate(self.board[:-1]):
						if 0 not in row:
							self.board = remove_row(self.board, i)
							break
					else:
						break
	
	def rotate_stone(self):
		if not self.gameover and not self.paused:
			new_stone = rotate_clockwise(self.stone)
			if not check_collision(self.board, new_stone, (self.stone_x, self.stone_y)):
				self.stone = new_stone
	
	def toggle_pause(self):
		self.paused = not self.paused
	
	def start_game(self):
		if self.gameover:
			self.init_game()
			self.gameover = False
	
	def run(self):
		key_actions = {
			'ESCAPE':	self.quit,
			'LEFT':		lambda:self.move(-1),
			'RIGHT':	lambda:self.move(+1),
			'DOWN':		self.drop,
			'UP':		self.rotate_stone,
			'p':		self.toggle_pause,
			'SPACE':	self.start_game
		}
		
		self.gameover = False
		self.paused = False
		
		pygame.time.set_timer(pygame.USEREVENT+1, config['delay'])
		dont_burn_my_cpu = pygame.time.Clock()
		while 1:
			self.screen.fill((0,0,0))
			if self.gameover:
				self.center_msg("""Game Over! Press space to continue""")
			else:
				if self.paused:
					self.center_msg("Paused")
				else:
					self.draw_matrix(self.board, (0,0))
					self.draw_matrix(self.stone, (self.stone_x, self.stone_y))
			pygame.display.update()
			
			for event in pygame.event.get():
				if event.type == pygame.USEREVENT+1:
					self.drop()
				elif event.type == pygame.QUIT:
					self.quit()
				elif event.type == pygame.KEYDOWN:
					for key in key_actions:
						if event.key == eval("pygame.K_" +key):
							key_actions[key]()
					
			dont_burn_my_cpu.tick(config['maxfps'])

if __name__ == '__main__':
	App = TetrisApp()
	App.run()
