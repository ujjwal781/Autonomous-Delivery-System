"""
Experimental framework for comparing pathfinding algorithms.
"""

import time
import json
import statistics
from typing import List, Dict, Any
from dataclasses import dataclass, asdict

from .environment import GridEnvironment
from .agent import DeliveryAgent
from .map_generator import MapGenerator

@dataclass
class ExperimentResult:
    """Results from a single experiment run."""
    map_name: str
    algorithm: str
    success: bool
    path_length: int
    total_cost: float
    total_time: int
    replanning_count: int
    nodes_expanded: int
    search_time: float
    execution_time: float

class ExperimentRunner:
    """Runs experiments comparing different algorithms."""
    
    def __init__(self):
        self.results: List[ExperimentResult] = []
    
    def run_single_experiment(self, env: GridEnvironment, algorithm: str, 
                            map_name: str, max_steps: int = 1000) -> ExperimentResult:
        """Run a single experiment with given environment and algorithm."""
        print(f"\nRunning {algorithm} on {map_name} map...")
        
        # Reset environment
        env.current_time = 0
        
        # Create agent
        agent = DeliveryAgent(env, algorithm)
        
        # Measure execution time
        start_time = time.time()
        success = agent.navigate_to_goal(env.goal_pos, max_steps)
        execution_time = time.time() - start_time
        
        # Get performance stats
        stats = agent.get_performance_stats()
        
        result = ExperimentResult(
            map_name=map_name,
            algorithm=algorithm,
            success=success,
            path_length=len(agent.path) if agent.path else 0,
            total_cost=stats['total_cost'],
            total_time=stats['total_time'],
            replanning_count=stats['replanning_count'],
            nodes_expanded=stats['total_nodes_expanded'],
            search_time=stats['total_search_time'],
            execution_time=execution_time
        )
        
        self.results.append(result)
        return result
    
    def run_algorithm_comparison(self, algorithms: List[str], runs_per_algorithm: int = 3):
        """Run comparison experiments across all algorithms and maps."""
        print("Starting algorithm comparison experiments...")
        
        # Generate test maps
        maps = {
            'small': MapGenerator.create_small_map(),
            'medium': MapGenerator.create_medium_map(),
            'large': MapGenerator.create_large_map(),
            'dynamic': MapGenerator.create_dynamic_map()
        }
        
        for map_name, env in maps.items():
            print(f"\n{'='*50}")
            print(f"Testing on {map_name} map ({env.width}x{env.height})")
            print(f"{'='*50}")
            
            for algorithm in algorithms:
                for run in range(runs_per_algorithm):
                    print(f"\nRun {run + 1}/{runs_per_algorithm} for {algorithm}")
                    try:
                        result = self.run_single_experiment(env, algorithm, map_name)
                        print(f"Result: {'SUCCESS' if result.success else 'FAILED'}, "
                              f"Cost: {result.total_cost:.2f}, "
                              f"Nodes: {result.nodes_expanded}, "
                              f"Time: {result.execution_time:.3f}s")
                    except Exception as e:
                        print(f"Error running {algorithm}: {e}")
    
    def analyze_results(self) -> Dict[str, Any]:
        """Analyze experimental results and generate statistics."""
        if not self.results:
            return {}
        
        analysis = {}
        
        # Group results by algorithm and map
        by_algorithm = {}
        by_map = {}
        
        for result in self.results:
            # By algorithm
            if result.algorithm not in by_algorithm:
                by_algorithm[result.algorithm] = []
            by_algorithm[result.algorithm].append(result)
            
            # By map
            if result.map_name not in by_map:
                by_map[result.map_name] = []
            by_map[result.map_name].append(result)
        
        # Algorithm performance analysis
        algorithm_stats = {}
        for algorithm, results in by_algorithm.items():
            successful_results = [r for r in results if r.success]
            
            if successful_results:
                algorithm_stats[algorithm] = {
                    'success_rate': len(successful_results) / len(results),
                    'avg_cost': statistics.mean(r.total_cost for r in successful_results),
                    'avg_nodes_expanded': statistics.mean(r.nodes_expanded for r in successful_results),
                    'avg_search_time': statistics.mean(r.search_time for r in successful_results),
                    'avg_execution_time': statistics.mean(r.execution_time for r in successful_results),
                    'avg_replanning': statistics.mean(r.replanning_count for r in successful_results),
                    'total_runs': len(results),
                    'successful_runs': len(successful_results)
                }
            else:
                algorithm_stats[algorithm] = {
                    'success_rate': 0,
                    'total_runs': len(results),
                    'successful_runs': 0
                }
        
        analysis['algorithm_performance'] = algorithm_stats
        analysis['by_map'] = by_map
        
        return analysis
    
    def generate_report(self, filename: str = 'experiment_report.json'):
        """Generate detailed experimental report."""
        analysis = self.analyze_results()
        
        report = {
            'experiment_summary': {
                'total_experiments': len(self.results),
                'algorithms_tested': list(set(r.algorithm for r in self.results)),
                'maps_tested': list(set(r.map_name for r in self.results))
            },
            'detailed_results': [asdict(result) for result in self.results],
            'analysis': analysis
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nExperiment report saved to {filename}")
        return report
    
    def print_summary(self):
        """Print a summary of experimental results."""
        analysis = self.analyze_results()
        
        print("\n" + "="*60)
        print("EXPERIMENTAL RESULTS SUMMARY")
        print("="*60)
        
        if 'algorithm_performance' in analysis:
            print("\nAlgorithm Performance:")
            print("-" * 40)
            
            for algorithm, stats in analysis['algorithm_performance'].items():
                print(f"\n{algorithm.upper()}:")
                print(f"  Success Rate: {stats['success_rate']:.2%}")
                if stats['success_rate'] > 0:
                    print(f"  Average Cost: {stats['avg_cost']:.2f}")
                    print(f"  Average Nodes Expanded: {stats['avg_nodes_expanded']:.0f}")
                    print(f"  Average Search Time: {stats['avg_search_time']:.4f}s")
                    print(f"  Average Execution Time: {stats['avg_execution_time']:.4f}s")
                    print(f"  Average Replanning Events: {stats['avg_replanning']:.1f}")
        
        print("\n" + "="*60)
