# Ride Share Simulator

## Purpose

This project aims to build an efficient ride share simulator using appropriate data structures and algorithms. Through the build up of this project, performance will be monitored through analysis and visualization. Algorithms will be appropriately utilized to implement effective path-finding and event management solutions.

## How to Run

If using a virtual environment, set up by running:
```bash
python3 -m venv .venv
```
Then activate it,
```bash
source .venv/bin/activate
```

To run the simulation,
```bash
python3 simulation.py
```

## Dependencies

None

## Map Data Format

The map data is captured in `map.csv`. Each row of this file represents a directed edge which contains values that represent the starting point, ending point, and travel time (i.e. weight) respectively. When the simulation is ran, the `map` attribute within Simulation instantiates a Graph passing the .csv file name as an argument to load the data into `map`.

## Pathfinding

Pathfinding is accomplished via Dijkstra's Algorithm. This is a greedy algorithm which works effectively on weighted graphs. The algorithm returns two dictionaries--Distances and Predecessors.
Predecessors is used by the `reconstruct_path()` method to return the path. Distances is used to obtain the value with the `end_node` key.

## Quadtree Data Structure

Quadtrees can be effective for partitioning 2D spatial problems. Points (e.g. cars and riders) can be inserted within the boundaries of a Quadtree. Defining the capacity of the quadtree determines when a node gets subdivided. If the points within a node exceeds the capacity, the node is divided into four smaller nodes with identical attributes. 

When searching for a closest neighbor to a given point, partitions closest to the given point are most relevant, speeding up the search. Large swaths of the map remain untouched if they are further than the closest neighbor found so far, and the time complexity approaches O(logN). If brute force were used to search for the closest neighbor, every point would need to be read giving an O(N) time complexity.

The `quadtree.py` file can be tested by running:

`pytest test_quadtree.py`