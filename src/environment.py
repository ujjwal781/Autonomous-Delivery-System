"""
Environment model for the autonomous delivery agent.
Handles grid representation, obstacles, terrain costs, and dynamic elements.
"""

import json
import random
from typing import List, Tuple, Dict, Optional, Set
from dataclasses import dataclass
from enum import Enum

class CellType(Enum):
    EMPTY = 0
    OBSTACLE = 1
    START = 2
    GOAL = 3
    AGENT = 4
    MOVING_OBSTACLE = 5

@dataclass
class MovingObstacle:
    """Represents a moving obstacle with position and movement pattern."""
    id: int
    positions: List[Tuple[int, int]]  # Sequence of positions over time
    current_step: int = 0
    
    def get_position_at_time(self, time: int) -> Tuple[int, int]:
        """Get obstacle position at given time step."""
        if not self.positions:
            return (-1, -1)
        return self.positions[time % len(self.positions)]
    
    def get_future_positions(self, start_time: int, horizon: int) -> Set[Tuple[int, int]]:
        """Get all positions this obstacle will occupy in the given time horizon."""
        positions = set()
        for t in range(start_time, start_time + horizon):
            positions.add(self.get_position_at_time(t))
        return positions

class GridEnvironment:
    """2D grid environment for delivery agent navigation."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid = [[CellType.EMPTY for _ in range(width)] for _ in range(height)]
        self.terrain_costs = [[1 for _ in range(width)] for _ in range(height)]
        self.start_pos: Optional[Tuple[int, int]] = None
        self.goal_pos: Optional[Tuple[int, int]] = None
        self.moving_obstacles: List[MovingObstacle] = []
        self.current_time = 0
        
    def set_cell(self, x: int, y: int, cell_type: CellType, cost: int = 1):
        """Set cell type and terrain cost."""
        if self.is_valid_position(x, y):
            self.grid[y][x] = cell_type
            self.terrain_costs[y][x] = cost
            
            if cell_type == CellType.START:
                self.start_pos = (x, y)
            elif cell_type == CellType.GOAL:
                self.goal_pos = (x, y)
    
    def set_terrain_cost(self, x: int, y: int, cost: int):
        """Set terrain cost for a cell."""
        if self.is_valid_position(x, y):
            self.terrain_costs[y][x] = cost
    
    def add_moving_obstacle(self, obstacle: MovingObstacle):
        """Add a moving obstacle to the environment."""
        self.moving_obstacles.append(obstacle)
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if position is within grid bounds."""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def is_passable(self, x: int, y: int, time: int = None) -> bool:
        """Check if a cell is passable at given time."""
        if not self.is_valid_position(x, y):
            return False
        
        # Check static obstacles
        if self.grid[y][x] == CellType.OBSTACLE:
            return False
        
        # Check moving obstacles at specific time
        if time is not None:
            for obstacle in self.moving_obstacles:
                if obstacle.get_position_at_time(time) == (x, y):
                    return False
        
        return True
    
    def get_terrain_cost(self, x: int, y: int) -> int:
        """Get terrain cost for a cell."""
        if self.is_valid_position(x, y):
            return self.terrain_costs[y][x]
        return float('inf')
    
    def get_neighbors(self, x: int, y: int, time: int = None) -> List[Tuple[int, int]]:
        """Get valid neighboring positions (4-connected)."""
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # up, right, down, left
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.is_passable(nx, ny, time):
                neighbors.append((nx, ny))
        
        return neighbors
    
    def update_time(self):
        """Advance time step for dynamic obstacles."""
        self.current_time += 1
    
    def get_moving_obstacle_positions(self, time: int) -> Set[Tuple[int, int]]:
        """Get all moving obstacle positions at given time."""
        positions = set()
        for obstacle in self.moving_obstacles:
            pos = obstacle.get_position_at_time(time)
            if pos != (-1, -1):
                positions.add(pos)
        return positions
    
    def save_to_file(self, filename: str):
        """Save environment to JSON file."""
        data = {
            'width': self.width,
            'height': self.height,
            'grid': [[cell.value for cell in row] for row in self.grid],
            'terrain_costs': self.terrain_costs,
            'start_pos': self.start_pos,
            'goal_pos': self.goal_pos,
            'moving_obstacles': [
                {
                    'id': obs.id,
                    'positions': obs.positions,
                    'current_step': obs.current_step
                }
                for obs in self.moving_obstacles
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load_from_file(cls, filename: str) -> 'GridEnvironment':
        """Load environment from JSON file."""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        env = cls(data['width'], data['height'])
        env.grid = [[CellType(cell) for cell in row] for row in data['grid']]
        env.terrain_costs = data['terrain_costs']
        env.start_pos = tuple(data['start_pos']) if data['start_pos'] else None
        env.goal_pos = tuple(data['goal_pos']) if data['goal_pos'] else None
        
        for obs_data in data.get('moving_obstacles', []):
            obstacle = MovingObstacle(
                id=obs_data['id'],
                positions=[tuple(pos) for pos in obs_data['positions']],
                current_step=obs_data.get('current_step', 0)
            )
            env.add_moving_obstacle(obstacle)
        
        return env
    
    def display(self, agent_pos: Optional[Tuple[int, int]] = None, time: int = None):
        """Display the current state of the environment."""
        if time is None:
            time = self.current_time
            
        moving_positions = self.get_moving_obstacle_positions(time)
        
        print(f"Environment at time {time}:")
        print("Legend: . = empty, # = obstacle, S = start, G = goal, A = agent, M = moving obstacle")
        print(f"Terrain costs shown in parentheses when > 1")
        print()
        
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                if agent_pos and (x, y) == agent_pos:
                    char = 'A'
                elif (x, y) in moving_positions:
                    char = 'M'
                elif self.grid[y][x] == CellType.OBSTACLE:
                    char = '#'
                elif self.grid[y][x] == CellType.START:
                    char = 'S'
                elif self.grid[y][x] == CellType.GOAL:
                    char = 'G'
                else:
                    char = '.'
                
                cost = self.terrain_costs[y][x]
                if cost > 1:
                    row += f"{char}({cost})"
                else:
                    row += f"{char}   "
                row += " "
            print(row)
        print()
