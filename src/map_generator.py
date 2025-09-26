"""
Map generator for creating test environments with various complexities.
"""

import random
import json
from typing import List, Tuple

from .environment import GridEnvironment, CellType, MovingObstacle

class MapGenerator:
    """Generates test maps with different characteristics."""
    
    @staticmethod
    def create_small_map() -> GridEnvironment:
        """Create a small 10x10 test map."""
        env = GridEnvironment(10, 10)
        
        # Set start and goal
        env.set_cell(1, 1, CellType.START)
        env.set_cell(8, 8, CellType.GOAL)
        
        # Add some obstacles
        obstacles = [(3, 2), (3, 3), (3, 4), (5, 5), (6, 5), (7, 5)]
        for x, y in obstacles:
            env.set_cell(x, y, CellType.OBSTACLE)
        
        # Add varied terrain costs
        for x in range(2, 5):
            for y in range(6, 9):
                env.set_terrain_cost(x, y, 3)  # Difficult terrain
        
        return env
    
    @staticmethod
    def create_medium_map() -> GridEnvironment:
        """Create a medium 20x20 test map."""
        env = GridEnvironment(20, 20)
        
        # Set start and goal
        env.set_cell(2, 2, CellType.START)
        env.set_cell(17, 17, CellType.GOAL)
        
        # Add maze-like obstacles
        for x in range(5, 15):
            env.set_cell(x, 8, CellType.OBSTACLE)
            env.set_cell(x, 12, CellType.OBSTACLE)
        
        # Add gaps in walls
        env.set_cell(7, 8, CellType.EMPTY)
        env.set_cell(12, 8, CellType.EMPTY)
        env.set_cell(9, 12, CellType.EMPTY)
        env.set_cell(14, 12, CellType.EMPTY)
        
        # Add varied terrain
        for x in range(0, 20):
            for y in range(0, 20):
                if random.random() < 0.2:  # 20% chance of difficult terrain
                    env.set_terrain_cost(x, y, random.randint(2, 4))
        
        return env
    
    @staticmethod
    def create_large_map() -> GridEnvironment:
        """Create a large 50x50 test map."""
        env = GridEnvironment(50, 50)
        
        # Set start and goal
        env.set_cell(5, 5, CellType.START)
        env.set_cell(44, 44, CellType.GOAL)
        
        # Add random obstacles (15% of cells)
        for x in range(50):
            for y in range(50):
                if (x, y) not in [(5, 5), (44, 44)] and random.random() < 0.15:
                    env.set_cell(x, y, CellType.OBSTACLE)
        
        # Add terrain variety
        for x in range(50):
            for y in range(50):
                if env.grid[y][x] != CellType.OBSTACLE:
                    terrain_type = random.random()
                    if terrain_type < 0.6:
                        cost = 1  # Normal terrain
                    elif terrain_type < 0.8:
                        cost = 2  # Moderate terrain
                    elif terrain_type < 0.95:
                        cost = 3  # Difficult terrain
                    else:
                        cost = 5  # Very difficult terrain
                    env.set_terrain_cost(x, y, cost)
        
        return env
    
    @staticmethod
    def create_dynamic_map() -> GridEnvironment:
        """Create a map with moving obstacles."""
        env = GridEnvironment(15, 15)
        
        # Set start and goal
        env.set_cell(1, 1, CellType.START)
        env.set_cell(13, 13, CellType.GOAL)
        
        # Add static obstacles
        static_obstacles = [(5, 3), (5, 4), (5, 5), (9, 7), (9, 8), (9, 9)]
        for x, y in static_obstacles:
            env.set_cell(x, y, CellType.OBSTACLE)
        
        # Add moving obstacles
        # Moving obstacle 1: horizontal movement
        moving_obs_1 = MovingObstacle(
            id=1,
            positions=[(i, 7) for i in range(2, 8)] + [(i, 7) for i in range(6, 1, -1)]
        )
        env.add_moving_obstacle(moving_obs_1)
        
        # Moving obstacle 2: vertical movement
        moving_obs_2 = MovingObstacle(
            id=2,
            positions=[(11, i) for i in range(3, 9)] + [(11, i) for i in range(7, 2, -1)]
        )
        env.add_moving_obstacle(moving_obs_2)
        
        # Moving obstacle 3: circular movement
        center_x, center_y = 7, 10
        radius = 2
        circular_positions = []
        for angle in range(0, 360, 45):  # 8 positions in circle
            x = center_x + int(radius * math.cos(math.radians(angle)))
            y = center_y + int(radius * math.sin(math.radians(angle)))
            if env.is_valid_position(x, y):
                circular_positions.append((x, y))
        
        if circular_positions:
            moving_obs_3 = MovingObstacle(id=3, positions=circular_positions)
            env.add_moving_obstacle(moving_obs_3)
        
        return env
    
    @staticmethod
    def save_all_test_maps():
        """Generate and save all test maps."""
        import os
        import math
        
        # Create maps directory
        os.makedirs('maps', exist_ok=True)
        
        # Generate and save maps
        maps = {
            'small': MapGenerator.create_small_map(),
            'medium': MapGenerator.create_medium_map(),
            'large': MapGenerator.create_large_map(),
            'dynamic': MapGenerator.create_dynamic_map()
        }
        
        for name, env in maps.items():
            filename = f'maps/{name}_map.json'
            env.save_to_file(filename)
            print(f"Saved {name} map to {filename}")
