import pygame
import sys
import math
from queue import Queue, PriorityQueue, LifoQueue

selected_algorithm = None

WIDTH = 700
HEIGHT = 800 

GRID_WIDTH = 600
GRID_HEIGHT = 600
MARGIN_TOP = 100  

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
BUTTON_COLOR = (180, 180, 180)
BUTTON_HOVER_COLOR = (150, 150, 150)

pygame.init()
pygame.mixer.init()
font = pygame.font.SysFont(None, 30)

pygame.mixer.music.load('mergemmaideparte.mp3') 

pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1) 

class Spot:
    def __init__(self, row, col, width):
        self.row = row
        self.col = col
        self.x = col * width + (WIDTH - GRID_WIDTH) // 2 
        self.y = row * width + MARGIN_TOP 
        self.color = WHITE
        self.neighbors = []
        self.width = width

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
        self.color = WHITE

    def make_closed(self):
        self.color = ORANGE

    def make_open(self):
        self.color = YELLOW

    def make_barrier(self):
        self.color = BLACK

    def make_start(self):
        self.color = RED

    def make_end(self):
        self.color = GREEN

    def make_path(self):
        self.color = TURQUOISE

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        total_rows = len(grid)
        total_cols = len(grid[0])

        if self.row < total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): #DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): #UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < total_cols - 1 and not grid[self.row][self.col + 1].is_barrier(): #RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): #LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False
    
class Button:
    def __init__(self, x, y, width, height, text, callback=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.callback = callback

    def draw(self, window, outline=None):
        mouse = pygame.mouse.get_pos()
        color = BUTTON_HOVER_COLOR if self.is_hovered(mouse) else BUTTON_COLOR
        pygame.draw.rect(window, color, (self.x, self.y, self.width, self.height))

        if outline:
            pygame.draw.rect(window, outline, (self.x, self.y, self.width, self.height), 2)

        text_surface = font.render(self.text, True, BLACK)
        window.blit(text_surface, (self.x + (self.width - text_surface.get_width()) // 2,
                                   self.y + (self.height - text_surface.get_height()) // 2))

    def is_hovered(self, mouse_pos):
        return self.x <= mouse_pos[0] <= self.x + self.width and self.y <= mouse_pos[1] <= self.y + self.height

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_hovered(pygame.mouse.get_pos()):
            if self.callback:
                self.callback()
            return True
        return False

class Dropdown:
    def __init__(self, x, y, width, height, options, main_text="Select Algorithm", on_select=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.options = options
        self.selected_option = main_text
        self.is_open = False
        self.on_select = on_select

    def draw(self, window):
        pygame.draw.rect(window, BUTTON_COLOR, (self.x, self.y, self.width, self.height))
        text_surface = font.render(self.selected_option, True, BLACK)
        window.blit(text_surface, (self.x + 5, self.y + (self.height - text_surface.get_height()) // 2))

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
                return True
            elif self.is_open:
                for index, option in enumerate(self.options):
                    option_rect = pygame.Rect(self.x, self.y + (index + 1) * self.height, self.width, self.height)
                    if option_rect.collidepoint(mouse_pos):
                        self.selected_option = option
                        self.is_open = False
                        if self.on_select:
                            self.on_select(option)
                        return True 
        return False 

    def is_hovered(self, mouse_pos):
        return self.x <= mouse_pos[0] <= self.x + self.width and self.y <= mouse_pos[1] <= self.y + self.height

def create_buttons_and_dropdown(grid, window):
    grid_start_x = (WIDTH - GRID_WIDTH) // 2 
    dropdown = Dropdown(grid_start_x, 30, 180, 40, ["BFS", "DFS", "UCS", "Dijkstra", "A*"], on_select=lambda algorithm: on_select_algorithm(algorithm))
    
    button_x_start = grid_start_x + GRID_WIDTH - 90
    buttons = [
        Button(button_x_start - 105, 30, 90, 40, "Reset", callback=lambda: on_reset(grid)),
        Button(button_x_start, 30, 90, 40, "Play", callback=lambda: on_play(window, grid, dropdown, buttons))
    ]
    return dropdown, buttons

def draw_buttons_and_dropdown(window, dropdown, buttons):
    dropdown.draw(window)
    for button in buttons:
        button.draw(window)    

def create_grid(rows, cols, width, height):
    grid = []
    gap = width // cols
    for i in range(rows):
        grid.append([])
        for j in range(cols):
            spot = Spot(i, j, gap)
            grid[i].append(spot)
    return grid

def draw_grid_lines(window, rows, cols, width, height):
    gap = width // cols
    start_x = (WIDTH - GRID_WIDTH) // 2
    for i in range(rows + 1):
        pygame.draw.line(window, BLACK, (start_x, MARGIN_TOP + i * gap), (start_x + width, MARGIN_TOP + i * gap))
    for j in range(cols + 1):
        pygame.draw.line(window, BLACK, (start_x + j * gap, MARGIN_TOP), (start_x + j * gap, MARGIN_TOP + height))

def draw(window, grid, dropdown, buttons):
    window.fill(PINK)
    
    for row in grid:
        for spot in row:
            spot.draw(window)
    
    draw_grid_lines(window, ROWS, COLS, GRID_WIDTH, GRID_HEIGHT)
    draw_buttons_and_dropdown(window, dropdown, buttons)
    
    pygame.display.update()

def on_reset(grid):
    global start, end
    for row in grid:
        for spot in row:
            spot.reset()
    start = None
    end = None

def clear_path(grid):
    for row in grid:
        for spot in row:
            if spot.is_open() or spot.is_closed() or spot.color == PINK: 
                spot.reset()

def on_play(window, grid, dropdown, buttons):
    global selected_algorithm, start, end
    if not start or not end:
        print("Start or end node is missing.")
        return
    
    clear_path(grid)
    
    for row in grid:
        for spot in row:
            spot.update_neighbors(grid)

    if selected_algorithm == "BFS":
        bfs(lambda: draw(window, grid, dropdown, buttons), grid, start, end)
    elif selected_algorithm == "DFS":
        dfs(lambda: draw(window, grid, dropdown, buttons), grid, start, end)
    elif selected_algorithm == "UCS":
        ucs(lambda: draw(window, grid, dropdown, buttons), grid, start, end)
    elif selected_algorithm == "Dijkstra":
        dijkstra(lambda: draw(window, grid, dropdown, buttons), grid, start, end)
    elif selected_algorithm == "A*":
        a_star(lambda: draw(window, grid, dropdown, buttons), grid, start, end, heuristic)
    else:
        print("No algorithm selected or implemented.")

def on_select_algorithm(algorithm):
    global selected_algorithm
    selected_algorithm = algorithm

def get_clicked_pos(pos, rows, cols, width, height):
    gap = width // cols
    x, y = pos
    start_x = (WIDTH - GRID_WIDTH) // 2
    if x < start_x or x >= start_x + width or y < MARGIN_TOP or y >= MARGIN_TOP + height:
        return None
    row = (y - MARGIN_TOP) // gap
    col = (x - start_x) // gap
    return row, col

def reconstruct_path(came_from, current, draw, start, end):
    while current in came_from:
        current = came_from[current]
        if current != start and current != end: 
            current.make_path()
        draw()

"""Algorithms""" 
def check_node(node, grid, visited):
    x, y = node.get_pos() 

    if x < 0 or x >= len(grid) or y < 0 or y >= len(grid[0]):
        return False 
    
    if grid[x][y].is_barrier():
        return False
    
    if node in visited: 
        return False

    return True

def bfs(draw, grid, start, end):
    tracking = Queue()
    tracking.put((start, [start]))
    visited = set()
    visited.add(start)

    while not tracking.empty(): 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current_node, path = tracking.get()
        if current_node == end:
            print("Path")
            print("Start")
            for step in path: 
                print(f"    ({step.row}, {step.col})")
            print("Goal")
            print(f"Length: {len(path) - 1} steps")
            reconstruct_path({step: path[idx - 1] for idx, step in enumerate(path) if idx > 0}, end, draw, start, end)            
            end.make_end()
            return True
        
        x, y = current_node.get_pos() 

        for neighbor in current_node.neighbors: 
            if check_node(neighbor, grid, visited):
                tracking.put((neighbor, path + [neighbor]))
                visited.add(neighbor)
                neighbor.make_open()
                draw()

        if current_node != start:
            current_node.make_closed()

    print("Path not found")
    return False

def dfs(draw, grid, start, end):
    stack = [(start, [start])] 
    visited = set()

    while stack:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current_node, path = stack.pop()

        if current_node == end:
            print("Path:")
            print("Start")
            for step in path:
                print(f"    ({step.row}, {step.col})")
            print("Goal")
            print(f"Length: {len(path) - 1} steps")
            reconstruct_path({step: path[idx - 1] for idx, step in enumerate(path) if idx > 0}, end, draw, start, end)
            end.make_end()
            return True

        if current_node not in visited:
            visited.add(current_node)

            if current_node != start:
                current_node.make_closed()

            for neighbor in current_node.neighbors:
                if neighbor not in visited and not neighbor.is_barrier():
                    stack.append((neighbor, path + [neighbor]))
                    if neighbor != start and neighbor != end:
                        neighbor.make_open()

            draw()

    print("Path not found")
    return False

def ucs(draw, grid, start, end): 
    priority_queue = PriorityQueue()
    priority_queue.put((0, start)) 
    
    distances = {spot: float("inf") for row in grid for spot in row}
    distances[start] = 0
    
    previous_nodes = {}
    
    visited = set() 

    while not priority_queue.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current_cost, current_node = priority_queue.get()

        if current_node == end:
            path = []
            while current_node in previous_nodes:
                path.append(current_node)
                current_node = previous_nodes[current_node]
            path.append(start)
            path.reverse()

            print("Path: ")
            print("Start: ")
            for step in path: 
                print(f"    ({step.row}, {step.col})")
            print("Goal")
            print(f"Length: {len(path) - 1} steps")
            reconstruct_path(previous_nodes, end, draw, start, end)
            end.make_end()
            return True
        
        if current_node in visited:
            continue

        visited.add(current_node)

        for neighbor in current_node.neighbors:
            new_cost = current_cost + 1

            if new_cost < distances[neighbor]:
                distances[neighbor] = new_cost
                priority_queue.put((new_cost, neighbor))
                previous_nodes[neighbor] = current_node

                if neighbor != start and neighbor != end:
                    neighbor.make_open()

        draw()
        if current_node != start:
            current_node.make_closed()

    print("Path not found")
    return False 

def dijkstra(draw, grid, start, end):
    priority_queue = PriorityQueue()
    priority_queue.put((0, start)) 
    
    distances = {spot: float("inf") for row in grid for spot in row}
    distances[start] = 0
    
    previous_nodes = {}
    
    visited = set() 

    while not priority_queue.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        current_cost, current_node = priority_queue.get()

        if current_node == end:
            path = []
            while current_node in previous_nodes:
                path.append(current_node)
                current_node = previous_nodes[current_node]
            path.append(start)
            path.reverse() 
            
            print("Path:")
            print("Start:")
            for step in path:
                print(f"    ({step.row}, {step.col}),")
            print("Goal")
            print(f"Length: {len(path) - 1} steps")  
            
            reconstruct_path(previous_nodes, end, draw, start, end)
            end.make_end()
            return True

        if current_node in visited:
            continue 
        
        visited.add(current_node)

        for neighbor in current_node.neighbors:
            path_cost = current_cost + 1 

            if path_cost < distances[neighbor]:
                distances[neighbor] = path_cost
                priority_queue.put((path_cost, neighbor))
                previous_nodes[neighbor] = current_node
                
                if neighbor != start and neighbor != end:
                    neighbor.make_open()
        
        draw()
        if current_node != start:
            current_node.make_closed()

    print("Path not found")
    return False

def a_star(draw, grid, start, end, heuristic):
    priority_queue = PriorityQueue()
    priority_queue.put((0, start))

    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0

    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = heuristic(start, end)

    prev_nodes = {}

    while not priority_queue.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current_node = priority_queue.get()[1]

        if current_node == end:
            path = []

            while current_node in prev_nodes:
                path.append(current_node)
                current_node = prev_nodes[current_node]
            path.append(start)
            path.reverse()

            print("Path")
            print("Start")
            for step in path:
                print(f"    ({step.row}, {step.col})")
            print("Goal")
            print(f"Length: {len(path) - 1} steps")
            reconstruct_path(prev_nodes, end, draw, start, end)
            end.make_end()
            return True
        
        for neighbor in current_node.neighbors:
            temp_g_score = g_score[current_node] + 1 

            if temp_g_score < g_score[neighbor]:
                prev_nodes[neighbor] = current_node
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + heuristic(neighbor, end)

                if neighbor not in [node[1] for node in priority_queue.queue]: 
                    priority_queue.put((f_score[neighbor], neighbor))
                    if neighbor != start and neighbor != end: 
                        neighbor.make_open()

        draw()
        if current_node != start: 
            current_node.make_closed()

    print("Path not found")
    return False

# Manhattan distance heuristic
def heuristic(node1, node2):
    x1, y1 = node1.get_pos()
    x2, y2 = node2.get_pos()
    return abs(x1 - x2) + abs(y1 - y2)

def main():
    global grid, start, end, selected_algorithm
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Visual Search Algorithms")

    grid = create_grid(ROWS, COLS, GRID_WIDTH, GRID_HEIGHT)
    start = None
    end = None
    selected_algorithm = None
    dropdown, buttons = create_buttons_and_dropdown(grid, window)

    running = True
    global paused
    paused = False

    while running:
        draw(window, grid, dropdown, buttons)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if dropdown.handle_event(event):
                continue

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row_col = get_clicked_pos(pos, ROWS, COLS, GRID_WIDTH, GRID_HEIGHT)
                if row_col:
                    row, col = row_col
                    spot = grid[row][col]

                    if not start and spot != end:
                        start = spot
                        start.make_start()
                    elif not end and spot != start:
                        end = spot
                        end.make_end()
                    elif spot != start and spot != end:
                        spot.make_barrier()

            if pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row_col = get_clicked_pos(pos, ROWS, COLS, GRID_WIDTH, GRID_HEIGHT)
                if row_col:
                    row, col = row_col
                    spot = grid[row][col]
                    spot.reset()
                    if spot == start:
                        start = None
                    elif spot == end:
                        end = None

            for button in buttons:
                button.is_clicked(event)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()