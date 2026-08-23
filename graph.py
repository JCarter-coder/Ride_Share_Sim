import csv
import collections
import math

class Graph:
  """
  City map containing road edges and graph-node coordinates
  """
  def __init__(self):
    self.adjacency_list = collections.defaultdict(list) # {}
    self.node_coordinates: dict = {}
    # To determine boundary of graph, initialize max origin, min dimensions
    self.x: float = math.inf
    self.y: float = math.inf
    self.width: float = 0.0
    self.height: float = 0.0

  # def add_vertex(self, vertex):
  #   if vertex not in self.adjacency_list:
  #     self.adjacency_list[vertex] = []

  # def add_edge(self, start_node, end_node, weight):
  #   self.add_vertex(start_node)
  #   self.add_vertex(end_node)
  #   self.adjacency_list[start_node].append((end_node, weight))

  def load_map_data(self, filename):
    # Used to determine the maximum points for width and height
    max_x: float = -math.inf
    max_y: float = -math.inf

    with open(filename, "r") as file:
      for line in file:
        if line.startswith("#") or not line.strip():
          continue

        data = line.strip().split(",")

        (
          start_id,
          start_x,
          start_y,
          end_id,
          end_x,
          end_y,
          weight
        ) = data

        self.node_coordinates[start_id] = (
          float(start_x),
          float(start_y)
        )

        self.node_coordinates[end_id] = (
          float(end_x),
          float(end_y)
        )

        self.adjacency_list[start_id].append(
          (end_id, float(weight))
        )

        self.adjacency_list[end_id].append(
          (start_id, float(weight))
        )

        # Determine the graph's origin to determine the boundary
        if float(start_x) < self.x:
          self.x = float(start_x)
        if float(end_x) < self.x:
          self.x = float(end_x)
        if float(start_y) < self.y:
          self.y = float(start_y)
        if float(end_y) < self.y:
          self.y = float(end_y)
        # Determine the graph's origin to determine the boundary
        if float(start_x) > max_x:
          max_x = float(start_x)
        if float(end_x) > max_x:
          max_x = float(end_x)
        if float(start_y) > max_y:
          max_y = float(start_y)
        if float(end_y) > max_y:
          max_y = float(end_y)

      self.width = max_x - self.x
      self.height = max_y - self.y

  # Snap coordinates to Graph Vertices
  def find_nearest_vertex(self, point: tuple) -> str | None:
    x_p, y_p = point
    shortest_distance = math.inf
    vertex = None

    for node, coordinates in self.node_coordinates.items():
      x_n, y_n = coordinates
      distance = (x_n - x_p)**2 + (y_n - y_p)**2
      if distance < shortest_distance:
        shortest_distance = distance
        vertex = node

    if vertex == None:
      raise ValueError("Graph vertices were not loaded.")

    return vertex

  # def load_from_file(self, filename):
  #   print(f"Loading map from {filename}...")
  #   try:
  #     with open(filename, 'r') as f:
  #       reader = csv.reader(f)
  #       for row in reader:
  #         if len(row) == 3:
  #           start, end, weight = row
  #           self.add_edge(str(start.strip()), str(end.strip()), int(weight.strip()))
  #     print("Map loaded successfully.")
  #   except FileNotFoundError:
  #     print(f"Error: file '{filename}' not found.")
  #   except Exception as e:
  #     print(f"An error occurred: {e}")

  def __str__(self):
    return f"""
Graph Adjacency List:

{"\n".join([f"{key} -> {val}" for key, val in self.adjacency_list.items()])}

{"\n".join([f"{key} -> {val}" for key, val in self.node_coordinates.items()])}
"""
