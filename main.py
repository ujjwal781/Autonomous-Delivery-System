"""
Main CLI interface for the autonomous delivery agent system.
"""

import argparse
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.environment import GridEnvironment
from src.agent import DeliveryAgent
from src.map_generator import MapGenerator
from src.experiment import ExperimentRunner

def run_single_delivery(args):
    """Run a single delivery simulation."""
    print(f"Loading map: {args.map}")
    
    try:
        env = GridEnvironment.load_from_file(args.map)
    except FileNotFoundError:
        print(f"Map file {args.map} not found!")
        return
    
    print(f"Using algorithm: {args.algorithm}")
    agent = DeliveryAgent(env, args.algorithm)
    
    print("Initial environment:")
    env.display()
    
    success = agent.navigate_to_goal(env.goal_pos, args.max_steps)
    
    print("\nFinal environment:")
    env.display(agent.position)
    
    # Print performance statistics
    stats = agent.get_performance_stats()
    print(f"\nPerformance Statistics:")
    print(f"Success: {success}")
    print(f"Total Cost: {stats['total_cost']}")
    print(f"Total Time: {stats['total_time']}")
    print(f"Replanning Events: {stats['replanning_count']}")
    print(f"Total Nodes Expanded: {stats['total_nodes_expanded']}")
    print(f"Total Search Time: {stats['total_search_time']:.4f}s")

def run_experiments(args):
    """Run experimental comparison of algorithms."""
    algorithms = args.algorithms.split(',')
    
    print(f"Running experiments with algorithms: {algorithms}")
    print(f"Runs per algorithm: {args.runs}")
    
    runner = ExperimentRunner()
    runner.run_algorithm_comparison(algorithms, args.runs)
    
    # Generate and save report
    report = runner.generate_report(args.output)
    runner.print_summary()

def generate_maps(args):
    """Generate test maps."""
    print("Generating test maps...")
    MapGenerator.save_all_test_maps()
    print("Test maps generated in 'maps/' directory")

def demonstrate_dynamic(args):
    """Demonstrate dynamic replanning."""
    print("Demonstrating dynamic replanning...")
    
    # Create dynamic map
    env = MapGenerator.create_dynamic_map()
    
    print("Dynamic map with moving obstacles:")
    env.display()
    
    # Test with temporal A*
    agent = DeliveryAgent(env, "temporal_astar")
    
    print("\nStarting navigation with Temporal A*...")
    success = agent.navigate_to_goal(env.goal_pos, 200)
    
    print(f"\nDynamic planning result: {'SUCCESS' if success else 'FAILED'}")
    stats = agent.get_performance_stats()
    print(f"Replanning events: {stats['replanning_count']}")
    
    # Show some time steps
    print("\nShowing environment at different time steps:")
    for t in [0, 5, 10, 15]:
        print(f"\nTime step {t}:")
        env.current_time = t
        env.display()

def main():
    parser = argparse.ArgumentParser(description="Autonomous Delivery Agent System")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Single delivery command
    single_parser = subparsers.add_parser('deliver', help='Run single delivery')
    single_parser.add_argument('--map', required=True, help='Map file path')
    single_parser.add_argument('--algorithm', default='astar', 
                              choices=['bfs', 'ucs', 'astar', 'temporal_astar', 'hill_climbing'],
                              help='Pathfinding algorithm')
    single_parser.add_argument('--max-steps', type=int, default=1000, 
                              help='Maximum steps before timeout')
    
    # Experiment command
    exp_parser = subparsers.add_parser('experiment', help='Run algorithm comparison')
    exp_parser.add_argument('--algorithms', default='bfs,ucs,astar,hill_climbing',
                           help='Comma-separated list of algorithms to test')
    exp_parser.add_argument('--runs', type=int, default=3,
                           help='Number of runs per algorithm')
    exp_parser.add_argument('--output', default='experiment_report.json',
                           help='Output file for results')
    
    # Generate maps command
    gen_parser = subparsers.add_parser('generate-maps', help='Generate test maps')
    
    # Dynamic demonstration command
    demo_parser = subparsers.add_parser('demo-dynamic', help='Demonstrate dynamic replanning')
    
    args = parser.parse_args()
    
    if args.command == 'deliver':
        run_single_delivery(args)
    elif args.command == 'experiment':
        run_experiments(args)
    elif args.command == 'generate-maps':
        generate_maps(args)
    elif args.command == 'demo-dynamic':
        demonstrate_dynamic(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
