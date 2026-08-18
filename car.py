from pathfinding import find_shortest_path
from graph import Graph
from rider import Rider

class Car:
  def __init__(self, id: str, location: tuple):
    self.id: str = id # string
    self.location: tuple = location # (x: float, y: float)
    self.status: str = "available" # "en_route_to_pickup", "en_route_to_destination"
    self.assigned_rider: Rider | None = None
    # self.destination: tuple | None = None
    self.route: list | None = None
    self.route_time: float | None = None
    self.busy_start_time = None
    self.total_busy_time: int = 0
    self.trips_completed: int = 0

  def __str__(self):
    # return f"\nCar {self.id} at {self.location} - Status: {self.status}."
    return (f"""Car {self.id} at {self.location} - Status: {self.status}.
Route {self.route} - Time: {self.route_time}
""")
  
  def calculate_route(self, destination: tuple, graph: Graph) -> None:
    start_node = self.location
    end_node = destination
    path, distance = find_shortest_path(graph, start_node, end_node)
    self.route = path
    self.route_time = distance