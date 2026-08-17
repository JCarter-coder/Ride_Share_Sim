import pytest
from car import Car
from graph import Graph

@pytest.fixture
def create_car():
  car = Car("CAR001", (10.0, 5.0))
  return car

@pytest.fixture
def create_graph():
  graph = Graph()
  graph.add_edge((10.0, 5.0), (20.0, 15.0), 10)
  graph.add_edge((20.0, 15.0), (30.0, 25.0), 15)
  graph.add_edge((30.0, 25.0), (15.0, 30.0), 15)
  graph.add_edge((10.0, 5.0), (15.0, 30.0), 41)
  return graph

def test_car_initialization(create_car):
  car = create_car
  assert car.id == "CAR001"
  assert car.location == (10.0, 5.0)
  assert car.status == "available"
  assert car.destination is None
  assert car.route is None
  assert car.route_time is None

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
