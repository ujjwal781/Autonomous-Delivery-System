"""
Autonomous delivery agent that uses pathfinding algorithms to navigate.
Handles dynamic replanning when obstacles are encountered.
"""

import time
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass

from .environment import GridEnvironment, CellType
from .algorithms import (
    PathfindingAlgorithm, BreadthFirstSearch, UniformCostSearch, 
    AStarSearch, TemporalAStar, HillClimbingReplanner, SearchResult
)

@dataclass
class DeliveryTask:
    """Represents a delivery task."""
    id: int
    pickup_location: Tuple[int, int]
    delivery_location: Tuple[int, int]
    priority: int = 1
    completed: bool = False

class DeliveryAgent:
    """Autonomous delivery agent with multiple pathfinding strategies."""
    
    def __init__(self, environment: GridEnvironment, algorithm: str = "astar"):
        self.environment = environment
        self.position = environment.start_pos
        self.algorithm_name = algorithm
        self.algorithm = self._create_algorithm(algorithm)
        self.path: List[Tuple[int, int]] = []
        self.path_index = 0
        self.total_cost = 0
        self.total_time = 0
        self.replanning_count = 0
        self.search_results: List[SearchResult] = []
        
    def _create_algorithm(self, algorithm: str) -> PathfindingAlgorithm:
        """Create pathfinding algorithm instance."""
        algorithms = {
            "bfs": BreadthFirstSearch,
            "ucs": UniformCostSearch,
            "astar": AStarSearch,
            "temporal_astar": TemporalAStar,
            "hill_climbing": HillClimbingReplanner
        }
        
        if algorithm not in algorithms:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        
        return algorithms[algorithm](self.environment)
    
    def plan_path(self, goal: Tuple[int, int], start_time: int = None) -> SearchResult:
        """Plan path from current position to goal."""
        if start_time is None:
            start_time = self.environment.current_time
            
        result = self.algorithm.find_path(self.position, goal, start_time)
        self.search_results.append(result)
        
        if result.success:
            self.path = result.path
            self.path_index = 0
            print(f"Planned path with {result.algorithm}: {len(result.path)} steps, "
                  f"cost: {result.cost:.2f}, nodes expanded: {result.nodes_expanded}")
        else:
            print(f"Failed to find path with {result.algorithm}")
            
        return result
    
    def execute_step(self) -> bool:
        """Execute one step of the current path."""
        if not self.path or self.path_index >= len(self.path):
            return False
        
        next_position = self.path[self.path_index]
        
        # Check if next position is still passable
        if not self.environment.is_passable(*next_position, self.environment.current_time):
            print(f"Obstacle detected at {next_position}! Replanning...")
            self.replanning_count += 1
            return self.replan()
        
        # Move to next position
        self.position = next_position
        self.path_index += 1
        
        # Add terrain cost
        terrain_cost = self.environment.get_terrain_cost(*self.position)
        self.total_cost += terrain_cost
        
        # Update environment time
        self.environment.update_time()
        self.total_time += 1
        
        print(f"Agent moved to {self.position} (cost: {terrain_cost}, total: {self.total_cost})")
        
        return True
    
    def replan(self) -> bool:
        """Replan path when obstacle is encountered."""
        if not self.path:
            return False
        
        goal = self.path[-1]  # Keep same goal
        result = self.plan_path(goal, self.environment.current_time)
        
        if result.success:
            print(f"Replanning successful! New path length: {len(self.path)}")
            return True
        else:
            print("Replanning failed!")
            return False
    
    def navigate_to_goal(self, goal: Tuple[int, int], max_steps: int = 1000) -> bool:
        """Navigate to goal with automatic replanning."""
        print(f"Starting navigation from {self.position} to {goal}")
        
        # Initial planning
        result = self.plan_path(goal)
        if not result.success:
            return False
        
        # Execute path with replanning
        steps = 0
        while self.position != goal and steps < max_steps:
            if not self.execute_step():
                break
            steps += 1
            
            # Display current state periodically
            if steps % 10 == 0:
                self.environment.display(self.position)
        
        success = self.position == goal
        if success:
            print(f"Goal reached! Total cost: {self.total_cost}, "
                  f"time: {self.total_time}, replanning events: {self.replanning_count}")
        else:
            print(f"Failed to reach goal within {max_steps} steps")
            
        return success
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics."""
        total_nodes_expanded = sum(r.nodes_expanded for r in self.search_results)
        total_search_time = sum(r.time_taken for r in self.search_results)
        
        return {
            'algorithm': self.algorithm_name,
            'total_cost': self.total_cost,
            'total_time': self.total_time,
            'replanning_count': self.replanning_count,
            'total_nodes_expanded': total_nodes_expanded,
            'total_search_time': total_search_time,
            'search_results': self.search_results
        }
    
    def reset(self):
        """Reset agent to initial state."""
        self.position = self.environment.start_pos
        self.path = []
        self.path_index = 0
        self.total_cost = 0
        self.total_time = 0
        self.replanning_count = 0
        self.search_results = []
        self.environment.current_time = 0
