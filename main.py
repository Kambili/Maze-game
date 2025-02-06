import pygame
import sys
from random import choice, randint
from pygame.locals import QUIT, KEYDOWN, K_UP, K_DOWN, K_LEFT, K_RIGHT
from queue import PriorityQueue

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
YELLOW = (255, 255, 0)  # AI agent color
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
        if 0 <= x < cols and 0 <= y < rows:
            return grid_cells[x + y * cols]
        return None

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

# A* Pathfinding Algorithm
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_search(start, goal):
    open_list = PriorityQueue()
    open_list.put((0, start))
    came_from = {start: None}
    g_score = {cell: float('inf') for cell in [(c.x, c.y) for c in grid_cells]}
    g_score[start] = 0

    while not open_list.empty():
        _, current = open_list.get()
        if current == goal:
            break
        x, y = current
        current_cell = grid_cells[x + y * cols]

        for direction, (dx, dy) in {'left': (-1, 0), 'right': (1, 0), 'top': (0, -1), 'bottom': (0, 1)}.items():
            if not current_cell.walls[direction]:
                neighbor = (x + dx, y + dy)
                if 0 <= neighbor[0] < cols and 0 <= neighbor[1] < rows:
                    temp_g_score = g_score[current] + 1
                    if temp_g_score < g_score[neighbor]:
                        g_score[neighbor] = temp_g_score
                        priority = temp_g_score + heuristic(neighbor, goal)
                        open_list.put((priority, neighbor))
                        came_from[neighbor] = current

    path = []
    step = goal
    while step:
        path.append(step)
        step = came_from.get(step)
    return path[::-1]

class Player:
    def __init__(self):
        self.grid_x = 0
        self.grid_y = 0

    def move_player(self, dx, dy):
        current_cell = grid_cells[self.grid_x + self.grid_y * cols]
        next_x = self.grid_x + dx
        next_y = self.grid_y + dy

        if next_x < 0 or next_x >= cols or next_y < 0 or next_y >= rows:
            return

        can_move = False
        if dx == -1:  # left
            can_move = not current_cell.walls['left']
        elif dx == 1:  # right
            can_move = not current_cell.walls['right']
        elif dy == -1:  # up
            can_move = not current_cell.walls['top']
        elif dy == 1:  # down
            can_move = not current_cell.walls['bottom']

        if can_move:
            self.grid_x = next_x
            self.grid_y = next_y

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, (self.grid_x * TILE + 5, self.grid_y * TILE + 5, TILE - 10, TILE - 10))

class AI:
    def __init__(self):
        self.grid_x = 0
        self.grid_y = 0
        self.path = []
        self.step = 0
        self.last_move_time = pygame.time.get_ticks()
        self.move_delay = 500

    def update_path(self, exit_pos):
        start = (self.grid_x, self.grid_y)
        self.path = a_star_search(start, exit_pos)
        self.step = 0

    def move(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time >= self.move_delay and self.step < len(self.path):
            self.grid_x, self.grid_y = self.path[self.step]
            self.step += 1
            self.last_move_time = current_time

    def draw(self, screen):
        pygame.draw.rect(screen, YELLOW, (self.grid_x * TILE + 5, self.grid_y * TILE + 5, TILE - 10, TILE - 10))

# Create grid and initialize variables
grid_cells = [Cell(col, row) for row in range(rows) for col in range(cols)]
current_cell = grid_cells[0]
current_cell.visited = True
stack = []

# Generate maze
while True:
    DISPLAYSURF.fill(BLUE)
    for cell in grid_cells:
        cell.draw()
    pygame.draw.rect(DISPLAYSURF, RED, (current_cell.x * TILE + 2, current_cell.y * TILE + 2, TILE - 4, TILE - 4))
    pygame.display.flip()
    clock.tick(1000)

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

# Make the first row open
for col in range(cols):
    grid_cells[col].walls['left'] = False
    grid_cells[col].walls['right'] = False

# Set random start and exit positions
player = Player()
player.grid_x, player.grid_y = randint(0, cols - 1), 0
exit_x, exit_y = randint(0, cols - 1), rows - 1

ai = AI()
ai.grid_x, ai.grid_y = player.grid_x, player.grid_y
ai.update_path((exit_x, exit_y))

# Game timer
start_time = pygame.time.get_ticks()

# Main game loop
running = True
while running:
    DISPLAYSURF.fill(BLUE)
    for cell in grid_cells:
        cell.draw()

    # Draw exit
    pygame.draw.rect(DISPLAYSURF, RED, (exit_x * TILE + 5, exit_y * TILE + 5, TILE - 10, TILE - 10))

    # Handle events
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_LEFT:
                player.move_player(-1, 0)
            elif event.key == K_RIGHT:
                player.move_player(1, 0)
            elif event.key == K_UP:
                player.move_player(0, -1)
            elif event.key == K_DOWN:
                player.move_player(0, 1)

    # Update AI
    ai.move()

    # Draw player and AI
    player.draw(DISPLAYSURF)
    ai.draw(DISPLAYSURF)

    # Check win condition
    if player.grid_x == exit_x and player.grid_y == exit_y:
        print("You Win!")
        running = False

    # Check time and if ai agent reaches first
    elapsed_time = pygame.time.get_ticks() - start_time
    if elapsed_time > 180000 or (ai.grid_x == exit_x and ai.grid_y == exit_y):
        print("You Lose! Time's up.")
        running = False

    # Display timer
    font = pygame.font.Font(None, 36)
    timer_text = font.render(f"Time Left: {max(180 - elapsed_time // 1000, 0)}s", True, BLACK)
    DISPLAYSURF.blit(timer_text, (WIDTH - 200, 10))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
