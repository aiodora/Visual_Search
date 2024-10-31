import pygame
import sys 
from algorithms import bfs, dfs, ucs, dijkstra, a_star 

WIDTH = 700
HEIGHT = 700
MARGIN_TOP = 150  
MARGIN_SIDES = 70  

GRID_WIDTH = WIDTH - 2 * MARGIN_SIDES
GRID_HEIGHT = HEIGHT - MARGIN_TOP - MARGIN_SIDES

ROWS = 40
COLS = 40

PINK = (255, 190, 220)
BLACK = (0, 0, 0)

pygame.init()

def draw_grid(window):
    cell_width = GRID_WIDTH / COLS
    cell_height = GRID_HEIGHT / ROWS

    for i in range(ROWS + 1):  
        y = MARGIN_TOP + i * cell_height
        pygame.draw.line(window, BLACK, (MARGIN_SIDES, y), (MARGIN_SIDES + GRID_WIDTH, y))

    for j in range(COLS + 1):  
        x = MARGIN_SIDES + j * cell_width
        pygame.draw.line(window, BLACK, (x, MARGIN_TOP), (x, MARGIN_TOP + GRID_HEIGHT))

def main(): 
    window = pygame.display.set_mode(size=(WIDTH, HEIGHT))
    pygame.display.set_caption("Visual Search Algorithms")
    window.fill(PINK)
    draw_grid(window) 

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()

if __name__ == "__main__": 
    main()
