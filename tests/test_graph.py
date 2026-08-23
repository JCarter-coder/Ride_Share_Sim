import pytest
from graph import Graph

@pytest.fixture
def load_graph():
  graph = Graph()
  graph.load_map_data("Final_Map_50_Node_Grid.csv")
  return graph

@pytest.fixture
def load_empty_graph():
  graph = Graph()
  return graph

def test_known_graph_size(load_graph):
  graph = load_graph
  assert len(graph.adjacency_list) == 50
  assert len(graph.node_coordinates) == 50

def test_node_coordinates(load_graph):
  graph = load_graph
  assert graph.node_coordinates["N0"] == (4.5598, 2.5509)
  assert graph.node_coordinates["N1"] == (1.5124, 0.6151)

def test_adjacency_list(load_graph):
  graph = load_graph
  assert len(graph.adjacency_list["N0"]) == 3
  assert len(graph.adjacency_list["N29"]) == 5

def test_graph_str_method(load_graph):
  graph = load_graph
  assert isinstance(graph.__str__(), str)

def test_find_nearest_vertex(load_graph):
  graph = load_graph
  nearest_vertex = graph.find_nearest_vertex((3.5, 6.5))
  assert nearest_vertex == "N49"

def test_raise_value_error(load_empty_graph):
  graph = load_empty_graph
  with pytest.raises(ValueError, match="Graph vertices were not loaded."):
    graph.find_nearest_vertex((3.5, 6.5))
