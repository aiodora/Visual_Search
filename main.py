import pygame
import sys 
import math
from algorithms import bfs, dfs, ucs, dijkstra, a_star 

WIDTH = 700
HEIGHT = 700
MARGIN_TOP = 150  
MARGIN_SIDES = 70 

GRID_WIDTH = WIDTH - 2 * MARGIN_SIDES
GRID_HEIGHT = HEIGHT - MARGIN_TOP - MARGIN_SIDES

ROWS = 40
COLS = 40

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PINK = (255, 190, 220)
ORANGE = (255, 120, 0)
TURQUOISE = (65, 225, 210)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 50)
WHITE = (255, 255, 255)
BUTTON_COLOR = (180, 180, 180)
BUTTON_HOVER_COLOR = (150, 150, 150) 

pygame.init()
font = pygame.font.SysFont(None, 30)

class Spot: 
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = col * width
        self.y = row * width 
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows 

    def get_pos(self):
        return self.row, self.col
    
    def is_closed(self):
        return self.color == ORANGE
    
    def is_open(self):
        return self.color == YELLOW
    
    def is_barrier(self):
        return self.color == BLACK 
    
    def is_start(self):
        return self.color == RED
    
    def is_end(self):
        return self.color == GREEN
    
    def reset(self):
        return self.color == WHITE
    
    def make_close(self):
        self.color = ORANGE
    
    def make_open(self):
        self.color = YELLOW

    def make_barrier(self):
        self.color == BLACK 
    
    def make_start(self):
        self.color == RED
    
    def make_end(self):
        self.color == GREEN

    def make_path(self):
        self.color = PINK

    def update_neighbors(self, grid):
        pass 

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x + MARGIN_SIDES, self.y + MARGIN_TOP, self.width, self.width))

    def __lt__(self, other):
        return False
    
class Button:
    def __init__(self, x, y, width, height, text):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, window, outline=None):
        # Draw the button with hover effect
        mouse = pygame.mouse.get_pos()
        if self.is_hovered(mouse):
            color = BUTTON_HOVER_COLOR
        else:
            color = BUTTON_COLOR

        pygame.draw.rect(window, color, (self.x, self.y, self.width, self.height))
        
        if outline:
            pygame.draw.rect(window, outline, (self.x, self.y, self.width, self.height), 2)

        text_surface = font.render(self.text, True, BLACK)
        window.blit(text_surface, (self.x + (self.width - text_surface.get_width()) // 2,
                                   self.y + (self.height - text_surface.get_height()) // 2))

    def is_hovered(self, mouse_pos):
        return self.x <= mouse_pos[0] <= self.x + self.width and self.y <= mouse_pos[1] <= self.y + self.height

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered(pygame.mouse.get_pos()):
                return True
        return False
    
class Dropdown:
    def __init__(self, x, y, width, height, options, main_text=" Select Algorithm"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.options = options
        self.selected_option = main_text
        self.is_open = False

    def draw(self, window):
        # Draw the main button
        pygame.draw.rect(window, BUTTON_COLOR, (self.x, self.y, self.width, self.height))
        text_surface = font.render(self.selected_option, True, BLACK)
        window.blit(text_surface, (self.x + 5, self.y + (self.height - text_surface.get_height()) // 2))

        # Draw the options if dropdown is open
        if self.is_open:
            for index, option in enumerate(self.options):
                pygame.draw.rect(window, BUTTON_COLOR, 
                                 (self.x, self.y + (index + 1) * self.height, self.width, self.height))
                option_text = font.render(option, True, BLACK)
                window.blit(option_text, (self.x + 5, self.y + (index + 1) * self.height + (self.height - option_text.get_height()) // 2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if self.is_hovered(mouse_pos):
                self.is_open = not self.is_open
            elif self.is_open:
                for index, option in enumerate(self.options):
                    option_rect = pygame.Rect(self.x, self.y + (index + 1) * self.height, self.width, self.height)
                    if option_rect.collidepoint(mouse_pos):
                        self.selected_option = option
                        self.is_open = False
                        return option
        return None

    def is_hovered(self, mouse_pos):
        return self.x <= mouse_pos[0] <= self.x + self.width and self.y <= mouse_pos[1] <= self.y + self.height

def draw_buttons(window, dropdown):
    dropdown.draw(window)
    control_buttons = [
        Button(WIDTH - 320, 20, 90, 40, "Reset"),
        Button(WIDTH - 220, 20, 90, 40, "Pause"),
        Button(WIDTH - 120, 20, 90, 40, "Replay")
    ]

    for button in control_buttons:
        button.draw(window)

    return control_buttons

def make_grid(rows, cols, grid_width, grid_height):
    grid = []
    cell_width = grid_width // cols
    cell_height = grid_height // rows

    for i in range(rows):
        grid.append([])
        for j in range(cols):
            spot = Spot(i, j, cell_width, rows)
            grid[i].append(spot)

    return grid

def draw_grid(window, grid):
    for row in grid:
        for spot in row:
            spot.draw(window)

    cell_width = GRID_WIDTH / COLS
    cell_height = GRID_HEIGHT / ROWS

    for i in range(ROWS + 1):  
        y = MARGIN_TOP + i * cell_height
        if y <= MARGIN_TOP + GRID_HEIGHT:
            pygame.draw.line(window, BLACK, (MARGIN_SIDES, y), (MARGIN_SIDES + GRID_WIDTH, y))

    for j in range(COLS + 1):  
        x = MARGIN_SIDES + j * cell_width
        if x <= MARGIN_SIDES + GRID_WIDTH:
            pygame.draw.line(window, BLACK, (x, MARGIN_TOP), (x, MARGIN_TOP + GRID_HEIGHT))

        pygame.draw.rect(window, PINK, (0, MARGIN_TOP + GRID_HEIGHT, WIDTH, HEIGHT - (MARGIN_TOP + GRID_HEIGHT)))

def draw(window, grid, dropdown, control_buttons):
    window.fill(PINK)
    draw_grid(window, grid)
    
    dropdown.draw(window)
    for button in control_buttons:
        button.draw(window)

    pygame.display.update()

def main():
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Visual Search Algorithms")

    grid = make_grid(ROWS, COLS, GRID_WIDTH, GRID_HEIGHT)
    dropdown = Dropdown(20, 20, 180, 40, ["BFS", "DFS", "UCS", "Dijkstra", "A*"])
    control_buttons = [
        Button(WIDTH - 320, 20, 90, 40, "Reset"),
        Button(WIDTH - 220, 20, 90, 40, "Pause"),
        Button(WIDTH - 120, 20, 90, 40, "Replay")
    ]

    running = True
    selected_algorithm = None
    paused = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            selected_option = dropdown.handle_event(event)
            if selected_option:
                print(f"Selected Algorithm: {selected_option}")

            for button in control_buttons:
                if button.is_clicked(event):
                    if button.text == "Reset":
                        print("Reset Button Clicked")
                        # Add reset logic here
                    elif button.text == "Pause":
                        paused = not paused
                        print(f"Pause Button Clicked. Paused: {paused}")
                    elif button.text == "Replay":
                        print("Replay Button Clicked")
                        # Add replay logic here

        # Draw everything
        draw(window, grid, dropdown, control_buttons)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()