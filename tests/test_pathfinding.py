import pytest
from pathfinding import find_shortest_path
from graph import Graph

@pytest.fixture
def load_graph():
  graph = Graph()
  graph.load_map_data("Final_Map_50_Node_Grid.csv")
  return graph

def test_find_shortest_path(load_graph):
  graph = load_graph
  path, distance = find_shortest_path(graph, 'N1', 'N19')
  assert distance == 19.0
  assert path == ['N1', 'N9', 'N19']