import heapq
import math

def dijkstra(graph, start_node):
  """
  Implements Dijkstra's algorithm to find the shortest path from a start node
  to all other nodes in a weighted graph.
  """
  distances = {node: math.inf for node in graph}
  distances[start_node] = 0

  predecessors = {node: None for node in graph}

  priority_queue = [(0, start_node)]

  while priority_queue:
    current_distance, current_node = heapq.heappop(priority_queue)

    if current_distance > distances[current_node]:
      continue

    for neighbor, weight in graph[current_node]:
      distance = current_distance + weight
      if distance < distances[neighbor]:
        distances[neighbor] = distance
        predecessors[neighbor] = current_node
        heapq.heappush(priority_queue, (distance, neighbor))
  print(f"Distances: {distances}")
  print(f"Predecessors: {predecessors}")
  return distances, predecessors

def reconstruct_path(predecessors, end_node):
  """
  Helper function to reconstruct the path from the predecessors dictionary
  """
  path = []
  current = end_node

  while current is not None:
    path.insert(0, current)
    current = predecessors[current]

  if len(path) == 1:
    return None

  return path

def find_shortest_path(graph, start_node, end_node):
  distances, predecessors = dijkstra(graph, start_node)
  path = reconstruct_path(predecessors, end_node)
  return path, distances[end_node]