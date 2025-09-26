"""
Generate analysis plots and visualizations from experimental results.
Note: This script shows the structure for analysis - actual plotting would require matplotlib.
"""

import json
import sys
import os

def analyze_results(results_file='experiment_report.json'):
    """Analyze experimental results and generate insights."""
    
    try:
        with open(results_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Results file {results_file} not found. Run experiments first.")
        return
    
    print("=== EXPERIMENTAL ANALYSIS ===\n")
    
    # Algorithm performance comparison
    if 'analysis' in data and 'algorithm_performance' in data['analysis']:
        perf = data['analysis']['algorithm_performance']
        
        print("Algorithm Performance Summary:")
        print("-" * 50)
        
        # Sort algorithms by success rate
        sorted_algs = sorted(perf.items(), key=lambda x: x[1].get('success_rate', 0), reverse=True)
        
        for alg_name, stats in sorted_algs:
            print(f"\n{alg_name.upper()}:")
            print(f"  Success Rate: {stats.get('success_rate', 0):.1%}")
            if stats.get('success_rate', 0) > 0:
                print(f"  Avg Cost: {stats.get('avg_cost', 0):.2f}")
                print(f"  Avg Nodes: {stats.get('avg_nodes_expanded', 0):.0f}")
                print(f"  Avg Time: {stats.get('avg_search_time', 0):.4f}s")
    
    # Map difficulty analysis
    print("\n\nMap Difficulty Analysis:")
    print("-" * 50)
    
    map_stats = {}
    for result in data.get('detailed_results', []):
        map_name = result['map_name']
        if map_name not in map_stats:
            map_stats[map_name] = {'total': 0, 'success': 0, 'avg_cost': 0, 'costs': []}
        
        map_stats[map_name]['total'] += 1
        if result['success']:
            map_stats[map_name]['success'] += 1
            map_stats[map_name]['costs'].append(result['total_cost'])
    
    for map_name, stats in map_stats.items():
        success_rate = stats['success'] / stats['total'] if stats['total'] > 0 else 0
        avg_cost = sum(stats['costs']) / len(stats['costs']) if stats['costs'] else 0
        
        print(f"\n{map_name.upper()} MAP:")
        print(f"  Success Rate: {success_rate:.1%}")
        print(f"  Average Cost: {avg_cost:.2f}")
        print(f"  Difficulty: {'High' if success_rate < 0.8 else 'Medium' if success_rate < 0.95 else 'Low'}")
    
    # Performance insights
    print("\n\nKey Insights:")
    print("-" * 50)
    
    insights = []
    
    if 'algorithm_performance' in data.get('analysis', {}):
        perf = data['analysis']['algorithm_performance']
        
        # Find best algorithm by success rate
        best_success = max(perf.items(), key=lambda x: x[1].get('success_rate', 0))
        insights.append(f"• {best_success[0]} has the highest success rate ({best_success[1].get('success_rate', 0):.1%})")
        
        # Find most efficient algorithm (lowest nodes expanded among successful ones)
        successful_algs = {k: v for k, v in perf.items() if v.get('success_rate', 0) > 0}
        if successful_algs:
            most_efficient = min(successful_algs.items(), 
                               key=lambda x: x[1].get('avg_nodes_expanded', float('inf')))
            insights.append(f"• {most_efficient[0]} is most computationally efficient "
                          f"({most_efficient[1].get('avg_nodes_expanded', 0):.0f} avg nodes)")
        
        # Find fastest algorithm
        if successful_algs:
            fastest = min(successful_algs.items(), 
                         key=lambda x: x[1].get('avg_search_time', float('inf')))
            insights.append(f"• {fastest[0]} is fastest "
                          f"({fastest[1].get('avg_search_time', 0):.4f}s avg search time)")
    
    for insight in insights:
        print(insight)
    
    print("\n=== ANALYSIS COMPLETE ===")

def main():
    """Main analysis function."""
    results_file = sys.argv[1] if len(sys.argv) > 1 else 'experiment_report.json'
    analyze_results(results_file)

if __name__ == '__main__':
    main()
