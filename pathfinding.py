import heapq
import math
from graph import Graph

def dijkstra(graph: Graph, start_node: str):
  """
  Implements Dijkstra's algorithm to find the shortest path from a start node
  to all other nodes in a weighted graph.
  """
  distances = {node: math.inf for node in graph.adjacency_list.keys()}
  distances[start_node] = 0

  predecessors = {node: None for node in graph.adjacency_list.keys()}

  priority_queue = [(0, start_node)]

  while priority_queue:
    current_distance, current_node = heapq.heappop(priority_queue)

    if current_distance > distances[current_node]:
      continue

    for neighbor, weight in graph.adjacency_list[current_node]:
      distance = current_distance + weight
      if distance < distances[neighbor]:
        distances[neighbor] = distance
        predecessors[neighbor] = current_node
        heapq.heappush(priority_queue, (distance, neighbor))
  #print(f"Distances: {distances}")
  #print(f"Predecessors: {predecessors}")
  return distances, predecessors

def reconstruct_path(predecessors, end_node):
  """
  Helper function to reconstruct the path from the predecessors dictionary
  """
  if end_node not in predecessors:
    raise ValueError(f"End node {end_node} does not exist in the graph.")
  path: list[str] = []
  current = end_node

  while current is not None:
    path.insert(0, current)
    current = predecessors[current]

  if len(path) == 1:
    return None

  return path

# Find the shortest path between two nodes
def find_shortest_path(graph: Graph, start_node: str, end_node: str):
  distances, predecessors = dijkstra(graph, start_node)
  path = reconstruct_path(predecessors, end_node)
  return path, distances[end_node]
