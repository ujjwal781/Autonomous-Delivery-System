"""
Pathfinding algorithms for the autonomous delivery agent.
Implements BFS, Uniform Cost Search, A*, and local search methods.
"""

import heapq
import random
import math
from typing import List, Tuple, Dict, Optional, Set
from abc import ABC, abstractmethod
from dataclasses import dataclass
from collections import deque

from .environment import GridEnvironment

@dataclass
class SearchResult:
    """Result of a pathfinding search."""
    path: List[Tuple[int, int]]
    cost: float
    nodes_expanded: int
    time_taken: float
    success: bool
    algorithm: str

@dataclass
class Node:
    """Node for search algorithms."""
    position: Tuple[int, int]
    g_cost: float  # Cost from start
    h_cost: float  # Heuristic cost to goal
    f_cost: float  # Total cost (g + h)
    parent: Optional['Node'] = None
    time: int = 0  # Time step for temporal planning
    
    def __lt__(self, other):
        return self.f_cost < other.f_cost

class PathfindingAlgorithm(ABC):
    """Abstract base class for pathfinding algorithms."""
    
    def __init__(self, environment: GridEnvironment):
        self.environment = environment
        self.nodes_expanded = 0
    
    @abstractmethod
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int], 
                  start_time: int = 0) -> SearchResult:
        """Find path from start to goal."""
        pass
    
    def reconstruct_path(self, node: Node) -> List[Tuple[int, int]]:
        """Reconstruct path from goal node to start."""
        path = []
        current = node
        while current:
            path.append(current.position)
            current = current.parent
        return path[::-1]
    
    def manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calculate Manhattan distance heuristic."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def euclidean_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calculate Euclidean distance heuristic."""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

class BreadthFirstSearch(PathfindingAlgorithm):
    """Breadth-First Search implementation."""
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int], 
                  start_time: int = 0) -> SearchResult:
        import time
        start_time_real = time.time()
        
        self.nodes_expanded = 0
        queue = deque([Node(start, 0, 0, 0)])
        visited = {start}
        
        while queue:
            current = queue.popleft()
            self.nodes_expanded += 1
            
            if current.position == goal:
                path = self.reconstruct_path(current)
                return SearchResult(
                    path=path,
                    cost=len(path) - 1,  # Number of moves
                    nodes_expanded=self.nodes_expanded,
                    time_taken=time.time() - start_time_real,
                    success=True,
                    algorithm="BFS"
                )
            
            for neighbor in self.environment.get_neighbors(*current.position):
                if neighbor not in visited:
                    visited.add(neighbor)
                    neighbor_node = Node(neighbor, 0, 0, 0, current)
                    queue.append(neighbor_node)
        
        return SearchResult([], float('inf'), self.nodes_expanded, 
                          time.time() - start_time_real, False, "BFS")

class UniformCostSearch(PathfindingAlgorithm):
    """Uniform Cost Search implementation."""
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int], 
                  start_time: int = 0) -> SearchResult:
        import time
        start_time_real = time.time()
        
        self.nodes_expanded = 0
        heap = [Node(start, 0, 0, 0)]
        visited = set()
        costs = {start: 0}
        
        while heap:
            current = heapq.heappop(heap)
            
            if current.position in visited:
                continue
                
            visited.add(current.position)
            self.nodes_expanded += 1
            
            if current.position == goal:
                path = self.reconstruct_path(current)
                return SearchResult(
                    path=path,
                    cost=current.g_cost,
                    nodes_expanded=self.nodes_expanded,
                    time_taken=time.time() - start_time_real,
                    success=True,
                    algorithm="UCS"
                )
            
            for neighbor in self.environment.get_neighbors(*current.position):
                terrain_cost = self.environment.get_terrain_cost(*neighbor)
                new_cost = current.g_cost + terrain_cost
                
                if neighbor not in costs or new_cost < costs[neighbor]:
                    costs[neighbor] = new_cost
                    neighbor_node = Node(neighbor, new_cost, 0, new_cost, current)
                    heapq.heappush(heap, neighbor_node)
        
        return SearchResult([], float('inf'), self.nodes_expanded, 
                          time.time() - start_time_real, False, "UCS")

class AStarSearch(PathfindingAlgorithm):
    """A* Search implementation with admissible heuristic."""
    
    def __init__(self, environment: GridEnvironment, heuristic='manhattan'):
        super().__init__(environment)
        self.heuristic_func = (self.manhattan_distance if heuristic == 'manhattan' 
                              else self.euclidean_distance)
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int], 
                  start_time: int = 0) -> SearchResult:
        import time
        start_time_real = time.time()
        
        self.nodes_expanded = 0
        start_h = self.heuristic_func(start, goal)
        heap = [Node(start, 0, start_h, start_h)]
        visited = set()
        costs = {start: 0}
        
        while heap:
            current = heapq.heappop(heap)
            
            if current.position in visited:
                continue
                
            visited.add(current.position)
            self.nodes_expanded += 1
            
            if current.position == goal:
                path = self.reconstruct_path(current)
                return SearchResult(
                    path=path,
                    cost=current.g_cost,
                    nodes_expanded=self.nodes_expanded,
                    time_taken=time.time() - start_time_real,
                    success=True,
                    algorithm="A*"
                )
            
            for neighbor in self.environment.get_neighbors(*current.position):
                terrain_cost = self.environment.get_terrain_cost(*neighbor)
                new_g_cost = current.g_cost + terrain_cost
                
                if neighbor not in costs or new_g_cost < costs[neighbor]:
                    costs[neighbor] = new_g_cost
                    h_cost = self.heuristic_func(neighbor, goal)
                    f_cost = new_g_cost + h_cost
                    neighbor_node = Node(neighbor, new_g_cost, h_cost, f_cost, current)
                    heapq.heappush(heap, neighbor_node)
        
        return SearchResult([], float('inf'), self.nodes_expanded, 
                          time.time() - start_time_real, False, "A*")

class TemporalAStar(PathfindingAlgorithm):
    """A* Search with temporal planning for dynamic obstacles."""
    
    def __init__(self, environment: GridEnvironment, planning_horizon: int = 50):
        super().__init__(environment)
        self.planning_horizon = planning_horizon
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int], 
                  start_time: int = 0) -> SearchResult:
        import time
        start_time_real = time.time()
        
        self.nodes_expanded = 0
        start_h = self.manhattan_distance(start, goal)
        heap = [Node(start, 0, start_h, start_h, time=start_time)]
        visited = set()
        costs = {}
        
        while heap:
            current = heapq.heappop(heap)
            
            state = (current.position, current.time)
            if state in visited:
                continue
                
            visited.add(state)
            self.nodes_expanded += 1
            
            if current.position == goal:
                path = self.reconstruct_path(current)
                return SearchResult(
                    path=path,
                    cost=current.g_cost,
                    nodes_expanded=self.nodes_expanded,
                    time_taken=time.time() - start_time_real,
                    success=True,
                    algorithm="Temporal A*"
                )
            
            # Don't plan too far into the future
            if current.time - start_time > self.planning_horizon:
                continue
            
            # Wait action (stay in place)
            next_time = current.time + 1
            if self.environment.is_passable(*current.position, next_time):
                wait_cost = current.g_cost + 1  # Cost of waiting
                wait_state = (current.position, next_time)
                if wait_state not in costs or wait_cost < costs[wait_state]:
                    costs[wait_state] = wait_cost
                    h_cost = self.manhattan_distance(current.position, goal)
                    f_cost = wait_cost + h_cost
                    wait_node = Node(current.position, wait_cost, h_cost, f_cost, 
                                   current, next_time)
                    heapq.heappush(heap, wait_node)
            
            # Move actions
            for neighbor in self.environment.get_neighbors(*current.position, next_time):
                terrain_cost = self.environment.get_terrain_cost(*neighbor)
                new_g_cost = current.g_cost + terrain_cost
                neighbor_state = (neighbor, next_time)
                
                if neighbor_state not in costs or new_g_cost < costs[neighbor_state]:
                    costs[neighbor_state] = new_g_cost
                    h_cost = self.manhattan_distance(neighbor, goal)
                    f_cost = new_g_cost + h_cost
                    neighbor_node = Node(neighbor, new_g_cost, h_cost, f_cost, 
                                       current, next_time)
                    heapq.heappush(heap, neighbor_node)
        
        return SearchResult([], float('inf'), self.nodes_expanded, 
                          time.time() - start_time_real, False, "Temporal A*")

class HillClimbingReplanner(PathfindingAlgorithm):
    """Hill climbing with random restarts for dynamic replanning."""
    
    def __init__(self, environment: GridEnvironment, max_restarts: int = 5):
        super().__init__(environment)
        self.max_restarts = max_restarts
        self.base_planner = AStarSearch(environment)
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int], 
                  start_time: int = 0) -> SearchResult:
        import time
        start_time_real = time.time()
        
        # First, try to find initial path with A*
        initial_result = self.base_planner.find_path(start, goal, start_time)
        if not initial_result.success:
            return initial_result
        
        best_path = initial_result.path
        best_cost = initial_result.cost
        total_nodes_expanded = initial_result.nodes_expanded
        
        # Hill climbing with random restarts
        for restart in range(self.max_restarts):
            current_path = self.perturb_path(best_path)
            current_cost = self.evaluate_path(current_path, start_time)
            
            if current_cost == float('inf'):
                continue
            
            # Hill climbing
            improved = True
            while improved:
                improved = False
                neighbors = self.get_path_neighbors(current_path)
                
                for neighbor_path in neighbors:
                    neighbor_cost = self.evaluate_path(neighbor_path, start_time)
                    total_nodes_expanded += 1
                    
                    if neighbor_cost < current_cost:
                        current_path = neighbor_path
                        current_cost = neighbor_cost
                        improved = True
                        break
            
            if current_cost < best_cost:
                best_path = current_path
                best_cost = current_cost
        
        return SearchResult(
            path=best_path,
            cost=best_cost,
            nodes_expanded=total_nodes_expanded,
            time_taken=time.time() - start_time_real,
            success=True,
            algorithm="Hill Climbing"
        )
    
    def perturb_path(self, path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Randomly perturb a path."""
        if len(path) < 3:
            return path
        
        new_path = path.copy()
        # Randomly modify a segment of the path
        start_idx = random.randint(1, len(path) - 2)
        end_idx = min(start_idx + random.randint(1, 3), len(path) - 1)
        
        # Try to find alternative route for this segment
        segment_start = path[start_idx - 1]
        segment_end = path[end_idx]
        
        # Simple random walk between segment points
        current = segment_start
        new_segment = [current]
        
        for _ in range(end_idx - start_idx + 2):
            neighbors = self.environment.get_neighbors(*current)
            if neighbors and segment_end in neighbors:
                new_segment.append(segment_end)
                break
            elif neighbors:
                current = random.choice(neighbors)
                new_segment.append(current)
            else:
                break
        
        if new_segment[-1] == segment_end:
            new_path = path[:start_idx] + new_segment[1:] + path[end_idx + 1:]
        
        return new_path
    
    def get_path_neighbors(self, path: List[Tuple[int, int]]) -> List[List[Tuple[int, int]]]:
        """Get neighboring paths by modifying single waypoints."""
        neighbors = []
        
        for i in range(1, len(path) - 1):  # Don't modify start or goal
            current_pos = path[i]
            for neighbor_pos in self.environment.get_neighbors(*current_pos):
                new_path = path.copy()
                new_path[i] = neighbor_pos
                if self.is_valid_path(new_path):
                    neighbors.append(new_path)
        
        return neighbors
    
    def is_valid_path(self, path: List[Tuple[int, int]]) -> bool:
        """Check if path is valid (consecutive positions are neighbors)."""
        for i in range(len(path) - 1):
            current = path[i]
            next_pos = path[i + 1]
            if next_pos not in self.environment.get_neighbors(*current):
                return False
        return True
    
    def evaluate_path(self, path: List[Tuple[int, int]], start_time: int) -> float:
        """Evaluate path cost considering terrain and dynamic obstacles."""
        if not self.is_valid_path(path):
            return float('inf')
        
        total_cost = 0
        for i, pos in enumerate(path):
            # Check for collision with moving obstacles
            time_step = start_time + i
            if not self.environment.is_passable(*pos, time_step):
                return float('inf')
            
            # Add terrain cost
            if i > 0:  # Don't count start position
                total_cost += self.environment.get_terrain_cost(*pos)
        
        return total_cost
