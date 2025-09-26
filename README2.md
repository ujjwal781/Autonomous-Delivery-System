# Autonomous Delivery Agent System

A comprehensive implementation of an autonomous delivery agent that navigates a 2D grid city using multiple pathfinding algorithms. The system demonstrates rational decision-making under constraints and handles dynamic obstacles through intelligent replanning.

## Features

### Environment Model
- **2D Grid World**: Configurable grid environments with varying terrain costs
- **Static Obstacles**: Fixed barriers that block movement
- **Dynamic Obstacles**: Moving obstacles with deterministic or unpredictable patterns
- **Terrain Variety**: Different movement costs (1-5) representing various terrain types
- **4-Connected Movement**: Agent moves up, down, left, right (diagonal movement optional)

### Pathfinding Algorithms

#### Uninformed Search
- **Breadth-First Search (BFS)**: Guarantees shortest path in terms of number of moves
- **Uniform Cost Search (UCS)**: Finds optimal path considering terrain costs

#### Informed Search
- **A* Search**: Uses admissible Manhattan distance heuristic for optimal pathfinding
- **Temporal A***: Extended A* that plans in space-time to handle moving obstacles

#### Local Search
- **Hill Climbing with Random Restarts**: Local search method for dynamic replanning
- **Path Perturbation**: Intelligent path modification for obstacle avoidance

### Agent Capabilities
- **Rational Decision Making**: Chooses actions that maximize delivery efficiency
- **Dynamic Replanning**: Automatically replans when obstacles are encountered
- **Performance Monitoring**: Tracks cost, time, nodes expanded, and replanning events
- **Multi-Algorithm Support**: Can switch between different pathfinding strategies

## Installation

1. Clone the repository:
\`\`\`bash
git clone <repository-url>
cd autonomous-delivery-agent
\`\`\`

2. No external dependencies required - uses only Python standard library

3. Generate test maps:
\`\`\`bash
python main.py generate-maps
\`\`\`

## Usage

### Command Line Interface

#### Single Delivery Simulation
\`\`\`bash
# Run delivery with A* algorithm
python main.py deliver --map maps/small_map.json --algorithm astar

# Run with different algorithm
python main.py deliver --map maps/dynamic_map.json --algorithm temporal_astar
\`\`\`

#### Algorithm Comparison Experiments
\`\`\`bash
# Compare all algorithms with default settings
python main.py experiment

# Custom experiment with specific algorithms
python main.py experiment --algorithms "bfs,astar,hill_climbing" --runs 5 --output my_results.json
\`\`\`

#### Dynamic Obstacle Demonstration
\`\`\`bash
# Show dynamic replanning in action
python main.py demo-dynamic
\`\`\`

#### Generate Test Maps
\`\`\`bash
# Create all test maps
python main.py generate-maps
\`\`\`

### Available Algorithms
- `bfs`: Breadth-First Search
- `ucs`: Uniform Cost Search  
- `astar`: A* Search with Manhattan heuristic
- `temporal_astar`: Temporal A* for dynamic obstacles
- `hill_climbing`: Hill climbing with random restarts

### Test Maps
- **Small Map** (10x10): Basic testing with simple obstacles
- **Medium Map** (20x20): Maze-like environment with varied terrain
- **Large Map** (50x50): Complex environment with random obstacles
- **Dynamic Map** (15x15): Moving obstacles with different movement patterns

## Architecture

### Core Components

1. **Environment (`src/environment.py`)**
   - Grid representation and obstacle management
   - Terrain cost modeling
   - Dynamic obstacle tracking
   - Time-based state management

2. **Algorithms (`src/algorithms.py`)**
   - Implementation of all pathfinding algorithms
   - Admissible heuristics
   - Search result tracking
   - Performance metrics

3. **Agent (`src/agent.py`)**
   - Autonomous navigation logic
   - Dynamic replanning capabilities
   - Performance monitoring
   - Multi-algorithm support

4. **Experiments (`src/experiment.py`)**
   - Automated testing framework
   - Statistical analysis
   - Performance comparison
   - Report generation

### Map File Format

Maps are stored in JSON format with the following structure:
\`\`\`json
{
  "width": 10,
  "height": 10,
  "grid": [[0, 0, 1, ...], ...],
  "terrain_costs": [[1, 1, 1, ...], ...],
  "start_pos": [1, 1],
  "goal_pos": [8, 8],
  "moving_obstacles": [
    {
      "id": 1,
      "positions": [[2, 3], [3, 3], [4, 3]],
      "current_step": 0
    }
  ]
}
\`\`\`

## Experimental Results

The system automatically generates comprehensive experimental reports including:

- **Success Rates**: Percentage of successful deliveries per algorithm
- **Path Costs**: Average terrain cost of found paths
- **Computational Efficiency**: Nodes expanded and search time
- **Replanning Statistics**: Frequency of dynamic replanning events
- **Scalability Analysis**: Performance across different map sizes

### Sample Results Structure
\`\`\`json
{
  "algorithm_performance": {
    "astar": {
      "success_rate": 1.0,
      "avg_cost": 15.2,
      "avg_nodes_expanded": 45,
      "avg_search_time": 0.0023,
      "avg_replanning": 2.1
    }
  }
}
\`\`\`

## Algorithm Analysis

### When Each Algorithm Performs Best

1. **BFS**: 
   - Best for: Unweighted grids, shortest path in moves
   - Limitations: Ignores terrain costs, high memory usage

2. **Uniform Cost Search**:
   - Best for: Weighted terrain, optimal cost paths
   - Limitations: No heuristic guidance, slower than A*

3. **A* Search**:
   - Best for: Static environments, optimal pathfinding
   - Limitations: Cannot handle dynamic obstacles directly

4. **Temporal A***:
   - Best for: Known dynamic obstacles, predictable movement
   - Limitations: Higher computational cost, requires future knowledge

5. **Hill Climbing**:
   - Best for: Dynamic replanning, unknown obstacle patterns
   - Limitations: May find suboptimal paths, local optima

## Testing and Reproducibility

### Running Tests
\`\`\`bash
# Generate reproducible test maps
python main.py generate-maps

# Run comprehensive experiments
python main.py experiment --runs 5

# Test dynamic replanning
python main.py demo-dynamic
\`\`\`

### Reproducibility Features
- Deterministic map generation with fixed seeds
- Consistent algorithm implementations
- Detailed logging of all decisions
- JSON-based result storage for analysis

## Dynamic Replanning Demonstration

The system includes a proof-of-concept dynamic replanning demonstration:

1. **Obstacle Detection**: Agent detects blocked path during execution
2. **Replanning Trigger**: Automatically initiates new path search
3. **Algorithm Selection**: Uses appropriate algorithm for dynamic conditions
4. **Execution Resume**: Continues navigation with new path

Example log output:
\`\`\`
Agent moved to (3, 4) (cost: 1, total: 4)
Obstacle detected at (4, 4)! Replanning...
Planned path with Temporal A*: 12 steps, cost: 18.00, nodes expanded: 67
Replanning successful! New path length: 12
\`\`\`

## Performance Metrics

The system tracks comprehensive performance metrics:

- **Path Quality**: Total cost, path length
- **Computational Efficiency**: Nodes expanded, search time
- **Adaptability**: Replanning frequency, success rate
- **Scalability**: Performance across map sizes
- **Robustness**: Handling of dynamic obstacles

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all existing tests pass
5. Submit a pull request

## License

This project is provided for educational and research purposes.
