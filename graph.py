import csv

"""
Representation of map.csv:


"""

class Graph:
  def __init__(self):
    self.adjacency_list = {}

  def add_vertex(self, vertex):
    if vertex not in self.adjacency_list:
      self.adjacency_list[vertex] = []

  def add_edge(self, start_node, end_node, weight):
    self.add_vertex(start_node)
    self.add_vertex(end_node)
    self.adjacency_list[start_node].append((end_node, weight))

  def load_from_file(self, filename):
    print(f"Loading map from {filename}...")
    try:
      with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
          if len(row) == 3:
            start, end, weight = row
            self.add_edge(str(start.strip()), str(end.strip()), int(weight.strip()))
      print("Map loaded successfully.")
    except FileNotFoundError:
      print(f"Error: file '{filename}' not found.")
    except Exception as e:
      print(f"An error occurred: {e}")

  def __str__(self):
    return f"""
    A
   / \\
  5   3
 /     \\
B       C
 \\     /
  4   1
   \\ /
    D

Graph Adjacency List:

{"\n".join([f"{key} -> {val}" for key, val in self.adjacency_list.items()])}
"""
