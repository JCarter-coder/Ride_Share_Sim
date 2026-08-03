from pathfinding import find_shortest_path

class Car:
  def __init__(self, id, initial_location):
    self.id = id # string
    self.location = initial_location # NOTE: changing to a node, no longer a tuple (x, y)
    self.status = "available" # en_route_to_pickup, en_route_to_destination, unavailable
    self.destination = None
    self.route = None
    self.route_time = None

  def __str__(self):
    # return f"\nCar {self.id} at {self.location} - Status: {self.status}."
    return (f"""Car {self.id} at {self.location} - Status: {self.status}.
Route {self.route} - Time: {self.route_time}
""")

  def calculate_route(self, destination, graph):
    start_node = self.location
    end_node = destination
    path, distance = find_shortest_path(graph, start_node, end_node)
    self.route = path
    self.route_time =distance

# car1 = Car("CAR001", (10, 5))
# car2 = Car("CAR002", (5, 6))

# print(car1)
# print(car2)