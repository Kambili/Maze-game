import pygame
import sys
from random import choice, randint
from pygame.locals import QUIT, KEYDOWN, K_UP, K_DOWN, K_LEFT, K_RIGHT

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 450
DISPLAYSURF = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption('Maze Runner Game')

# Define variables
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
TILE = 25
cols, rows = WIDTH // TILE, HEIGHT // TILE

# Define Cell class
class Cell:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False

    def draw(self):
        x, y = self.x * TILE, self.y * TILE
        if self.visited:
            pygame.draw.rect(DISPLAYSURF, WHITE, (x, y, TILE, TILE))
        if self.walls['top']:
            pygame.draw.line(DISPLAYSURF, BLACK, (x, y), (x + TILE, y), 3)
        if self.walls['right']:
            pygame.draw.line(DISPLAYSURF, BLACK, (x + TILE, y), (x + TILE, y + TILE), 3)
        if self.walls['bottom']:
            pygame.draw.line(DISPLAYSURF, BLACK, (x + TILE, y + TILE), (x, y + TILE), 3)
        if self.walls['left']:
            pygame.draw.line(DISPLAYSURF, BLACK, (x, y + TILE), (x, y), 3)

    def check_cell(self, x, y):
        find_index = lambda x, y: x + y * cols
        if x < 0 or x >= cols or y < 0 or y >= rows:
            return None
        return grid_cells[find_index(x, y)]

    def check_neighbours(self):
        neighbors = []
        top = self.check_cell(self.x, self.y - 1)
        right = self.check_cell(self.x + 1, self.y)
        bottom = self.check_cell(self.x, self.y + 1)
        left = self.check_cell(self.x - 1, self.y)
        if top and not top.visited:
            neighbors.append(top)
        if right and not right.visited:
            neighbors.append(right)
        if bottom and not bottom.visited:
            neighbors.append(bottom)
        if left and not left.visited:
            neighbors.append(left)
        return choice(neighbors) if neighbors else None

    def remove_walls(self, next):
        dx, dy = self.x - next.x, self.y - next.y
        if dx == 1:
            self.walls['left'] = False
            next.walls['right'] = False
        elif dx == -1:
            self.walls['right'] = False
            next.walls['left'] = False
        if dy == 1:
            self.walls['top'] = False
            next.walls['bottom'] = False
        elif dy == -1:
            self.walls['bottom'] = False
            next.walls['top'] = False

# Create grid and initialize variables
grid_cells = [Cell(col, row) for row in range(rows) for col in range(cols)]
current_cell = grid_cells[0]
current_cell.visited = True
stack = []

# Generate maze
while True:
    next_cell = current_cell.check_neighbours()
    if next_cell:
        next_cell.visited = True
        stack.append(current_cell)
        current_cell.remove_walls(next_cell)
        current_cell = next_cell
    elif stack:
        current_cell = stack.pop()
    else:
        break

# Make the first row completely open
for col in range(cols):
    grid_cells[col].walls['top'] = False  # Remove top wall
    grid_cells[col].walls['left'] = False  # Remove left wall
    grid_cells[col].walls['right'] = False  # Remove right wall
    # Do NOT remove the bottom wall to prevent skipping rows

# Set random start position in the first row
player_x = randint(0, cols - 1)
player_y = 0

# Set a single exit at a random position in the last row
exit_x = randint(0, cols - 1)
exit_y = rows - 1

def move_player(dx, dy):
    global player_x, player_y
    next_cell = grid_cells[player_x + dx + (player_y + dy) * cols]
    current_cell = grid_cells[player_x + player_y * cols]
    if dx == -1 and not current_cell.walls['left']:
        player_x -= 1
    elif dx == 1 and not current_cell.walls['right']:
        player_x += 1
    elif dy == -1 and not current_cell.walls['top']:
        player_y -= 1
    elif dy == 1 and not current_cell.walls['bottom']:
        player_y += 1

# Main game loop
running = True
while running:
    DISPLAYSURF.fill(BLUE)
    for cell in grid_cells:
        cell.draw()
    pygame.draw.rect(DISPLAYSURF, GREEN, (player_x * TILE + 5, player_y * TILE + 5, TILE - 10, TILE - 10))
    pygame.draw.rect(DISPLAYSURF, RED, (exit_x * TILE + 5, exit_y * TILE + 5, TILE - 10, TILE - 10))

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_LEFT:
                move_player(-1, 0)
            elif event.key == K_RIGHT:
                move_player(1, 0)
            elif event.key == K_UP:
                move_player(0, -1)
            elif event.key == K_DOWN:
                move_player(0, 1)

    # Check if player reached the exit
    if player_x == exit_x and player_y == exit_y:
        print("You Win!")
        running = False

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
