import pytest
from car import Car
from graph import Graph

@pytest.fixture
def create_car():
  car = Car("CAR001", (1.5120, 0.6155))
  return car

@pytest.fixture
def load_graph():
  graph = Graph()
  graph.load_map_data("Final_Map_50_Node_Grid.csv")
  return graph

# @pytest.fixture
# def create_graph():
#   graph = Graph()
#   graph.add_edge((10.0, 5.0), (20.0, 15.0), 10)
#   graph.add_edge((20.0, 15.0), (30.0, 25.0), 15)
#   graph.add_edge((30.0, 25.0), (15.0, 30.0), 15)
#   graph.add_edge((10.0, 5.0), (15.0, 30.0), 41)
#   return graph

def test_car_initialization(create_car):
  car = create_car
  assert car.id == "CAR001"
  assert car.location == (1.5120, 0.6155)
  assert car.status == "available"
  assert car.assigned_rider is None
  assert car.route is None
  assert car.route_time is None
  assert car.busy_start_time is None
  assert car.total_busy_time == 0
  assert car.trips_completed == 0

def test_car_calculate_route(load_graph, create_car):
  graph = load_graph
  car = create_car
  car.calculate_route((3.4116, 1.4264), graph)
  assert car.route == ['N1', 'N9', 'N19']
  assert car.route_time == 19.0

def test_car_str(create_car):
  car = create_car
  expected_str = f"""Car {car.id} at {car.location} - Status: {car.status}.\nRoute {car.route} - Time: {car.route_time}
"""
  assert str(car) == expected_str

# def test_calculate_route(create_car, create_graph):
#   car = create_car
#   graph = create_graph
#   destination = (15.0, 30.0)
#   car.calculate_route(destination, graph)
#   assert car.route == [(10.0, 5.0), (20.0, 15.0), (30.0, 25.0), (15.0, 30.0)]
#   assert car.route_time == 40
