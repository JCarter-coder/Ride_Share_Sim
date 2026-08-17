from pathfinding import find_shortest_path
from graph import Graph
from rider import Rider

class Car:
  def __init__(self, id: str, location: tuple):
    self.id: str = id # string
    self.location: tuple = location # (x, y)
    self.status: str = "available" # en_route_to_pickup, en_route_to_destination, unavailable
    self.assigned_rider: Rider | None = None
    self.destination: tuple | None = None
    self.route: list | None = None
    self.route_time: float | None = None

  def __str__(self):
    # return f"\nCar {self.id} at {self.location} - Status: {self.status}."
    return (f"""Car {self.id} at {self.location} - Status: {self.status}.
Route {self.route} - Time: {self.route_time}
""")
  
  def calculate_route(self, destination, graph: Graph):
    start_node = self.location
    end_node = destination
    path, distance = find_shortest_path(graph, start_node, end_node)
    self.route = path
    self.route_time = distance