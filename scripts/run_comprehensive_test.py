"""
Comprehensive test script that demonstrates all system capabilities.
"""

import sys
import os
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.environment import GridEnvironment
from src.agent import DeliveryAgent
from src.map_generator import MapGenerator
from src.experiment import ExperimentRunner

def main():
    print("=== AUTONOMOUS DELIVERY AGENT COMPREHENSIVE TEST ===\n")
    
    # 1. Generate test maps
    print("1. Generating test maps...")
    MapGenerator.save_all_test_maps()
    print("✓ Test maps generated\n")
    
    # 2. Test single algorithm on each map
    print("2. Testing individual algorithms...")
    
    maps = ['small', 'medium', 'large', 'dynamic']
    algorithms = ['bfs', 'ucs', 'astar', 'temporal_astar', 'hill_climbing']
    
    for map_name in maps:
        print(f"\nTesting on {map_name} map:")
        try:
            env = GridEnvironment.load_from_file(f'maps/{map_name}_map.json')
            
            # Test A* as representative algorithm
            agent = DeliveryAgent(env, 'astar')
            success = agent.navigate_to_goal(env.goal_pos, 500)
            
            stats = agent.get_performance_stats()
            print(f"  Result: {'SUCCESS' if success else 'FAILED'}")
            print(f"  Cost: {stats['total_cost']:.2f}")
            print(f"  Nodes expanded: {stats['total_nodes_expanded']}")
            print(f"  Replanning events: {stats['replanning_count']}")
            
        except Exception as e:
            print(f"  Error: {e}")
    
    # 3. Run comparative experiments
    print("\n3. Running comparative experiments...")
    
    runner = ExperimentRunner()
    runner.run_algorithm_comparison(['bfs', 'astar', 'hill_climbing'], runs_per_algorithm=2)
    
    # Generate report
    report = runner.generate_report('comprehensive_test_results.json')
    runner.print_summary()
    
    # 4. Demonstrate dynamic replanning
    print("\n4. Demonstrating dynamic replanning...")
    
    env = MapGenerator.create_dynamic_map()
    agent = DeliveryAgent(env, 'temporal_astar')
    
    print("Initial state:")
    env.display()
    
    success = agent.navigate_to_goal(env.goal_pos, 100)
    stats = agent.get_performance_stats()
    
    print(f"\nDynamic replanning result: {'SUCCESS' if success else 'FAILED'}")
    print(f"Replanning events: {stats['replanning_count']}")
    
    print("\n=== COMPREHENSIVE TEST COMPLETED ===")
    print("Check 'comprehensive_test_results.json' for detailed results")

if __name__ == '__main__':
    main()
