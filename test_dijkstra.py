from pathfinding import find_shortest_path
from graph import Graph

if __name__ == "__main__":
  city_map = Graph()
  city_map.load_from_file('map.csv')
  graph = city_map.adjacency_list

  print(graph)

  start_location = "A"
  final_location = "D"
  path, distance = find_shortest_path(graph, start_location, final_location)

  print(f"Finding shortest path from node '{start_location}' to node '{final_location}'...\n")
  print(f"Path: {path}")
  print(f"Final Distance: {distance}")
