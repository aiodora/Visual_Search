from inspect import stack
from queue import Queue, PriorityQueue, LifoQueue

def check_node(node, grid, visited):
    x, y = node 

    if x < 0 or x >= len(grid) or y < 0 or y >= len(grid[0]):
        return False 
    
    if grid[x][y] == -1:
        return False
    
    if node in visited: 
        return False

    return True

def bfs(grid, start, end):
    tracking = Queue()
    tracking.put((start, [start]))
    visited = set()
    visited.add(start)

    while not tracking.empty(): 
        current_node, path = tracking.get()
        if current_node == end:
            return path
        
        x, y = current_node 

        for neighbor in [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]: 
            if check_node(neighbor, grid, visited):
                tracking.put((neighbor, path + [neighbor]))
                visited.add(neighbor)

    return []

def dfs(grid, start, end):
    tracking = LifoQueue()
    tracking.put((start, [start]))
    visited = set()
    visited.add(start)

    while not tracking.empty(): 
        current_node, path = tracking.get()
        if current_node == end:
            return path
        
        x, y = current_node

        for neighbor in [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]: 
            if check_node(neighbor, grid, visited):
                tracking.put((neighbor, path + [neighbor]))
                visited.add(neighbor)

    return []

def ucs(grid, start, end): 

    return

def dijkstra(grid, start, end):

    return

def a_star(grid, start, end, heuristic):

    return

#Manhattan distance 
def heuristic(node, end):
    return abs(node[0] - end[0]) + abs(node[1] - end[1])
