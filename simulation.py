import argparse
import heapq
import math
import random
from dataclasses import dataclass, field
from enum import Enum, auto
from itertools import count
from car import Car
from rider import Rider
from graph import Graph
from quadtree import Quadtree, Rectangle, Point
from pathfinding import find_shortest_path

# Default settings
TRAVEL_SPEED_FACTOR: int = 1
DEFAULT_MAP: str = 'Final_Map_1000_Node_Grid.csv'
DEFAULT_MAX_TIME: int = 20
DEFAULT_MAX_RIDERS: int = 5
DEFAULT_CANDIDATE_COUNT: int = 5 # k-value
MEAN_ARRIVAL_TIME: int = 5

class EventStatus(Enum):
  RIDER_REQUEST = auto()
  PICKUP_ARRIVAL = auto()
  DROPOFF_ARRIVAL = auto()

@dataclass(order=True) # generates six comparison methods based on the order of the fields
class Event:
  timestamp: int
  sequence_number: int
  event_type: str # 'RIDE_REQUEST', 'TRIP_COMPLETION', etc.
  data: Rider | Car = field(compare=False) # Field ignored when ordering events in the priority queue

class Simulation:
  def __init__(self, map_filename, max_time=DEFAULT_MAX_TIME, num_riders=DEFAULT_MAX_RIDERS):
    self.current_time: int = 0
    self.event_queue: list[Event] = []
    self.sequence_number: int = count()
    self.cars: dict[str, Car] = {}
    self.available_cars: dict[str, Car] = {} # { car.id: Car, ... }
    self.available_car_points: dict[str, Point] = {} # { car.id: Point, ... }
    self.map = Graph()
    self.map.load_map_data(map_filename)
    self.boundary = Rectangle(self.map.x, self.map.y, self.map.width, self.map.height)
    self.available_car_quadtree = Quadtree(self.boundary) # For spatial index of available cars
    self.riders: dict[Rider] = {}
    self.car_waiting_queue: dict[Car] = {} # used if car does not find a rider match
    self.rider_waiting_queue: dict[Rider] = {} # used if rider does not find a car match
    
    # Default settings
    self.car_id_num: int = 1
    self.rider_id_num: int = 1
    self.num_cars: int = 5
    self.num_riders: int = num_riders
    self.max_time: int = max_time
    self.candidate_count: int = DEFAULT_CANDIDATE_COUNT

  def generate_cars(self) -> None:
    cars_created = 0
    while cars_created < self.num_cars:
      # Generate a Car
      car_id = "Car-" + str(self.car_id_num)
      x_min = self.boundary.x
      y_min = self.boundary.y
      x_max = self.boundary.width
      y_max = self.boundary.height
      location = (random.uniform(x_min, x_max), random.uniform(y_min, y_max))
      car = Car(car_id, location)
      self.cars[car.id] = car
      # Add to available car dict
      self.add_available_car(car)
      # Increment initial values
      self.car_id_num += 1
      cars_created += 1

  def add_available_car(self, car: Car) -> None:
    # Convert tuple into a Point
    x, y = car.location
    car_point = Point(x, y, data=car)
    if (
      car.id not in self.available_cars and
      car.id not in self.available_car_points and
      self.boundary.contains(car_point)
    ):
      
      car_point = Point(
        x,
        y,
        data=car
      )
      is_successful = self.available_car_quadtree.root.insert(car_point)
      # If inserted into quadtree successfully, update dicts and car status
      if is_successful:
        self.available_cars[car.id] = car
        self.available_car_points[car.id] = car_point
        car.status = "available"
      else: 
        print(f"REPORT: add_available_car({car.id}) unsuccessful...")

  def remove_available_car(self, car: Car) -> None:
    car_point_to_remove = self.available_car_points.get(car.id)

    if car_point_to_remove is None:
      return
    
    is_successful = self.available_car_quadtree.root.remove(car_point_to_remove)
    # If removed from quadtree successfully, pop from available car points
    if is_successful:
      self.available_car_points.pop(car.id, None)
      self.available_cars.pop(car.id, None)
    else: 
      print(f"REPORT: remove_available_car({car.id}) unsuccessful...")

  def generate_rider_request(self):
    request_time = self.current_time # Begins at initial value of 0
    current_num_riders = 0
    while current_num_riders < self.num_riders:
      # If max time is not exceeded, generate riders
      if request_time >= self.max_time:
        print("Time is up!")
        break

      # Generate a Rider
      rider_id = "Rider-" + str(self.rider_id_num)

      x_min = self.boundary.x
      y_min = self.boundary.y
      x_max = self.boundary.x + self.boundary.width
      y_max = self.boundary.y + self.boundary.height

      start = (random.uniform(x_min, x_max), random.uniform(y_min, y_max))
      destination = (random.uniform(x_min, x_max), random.uniform(y_min, y_max))

      rider = Rider(rider_id, start, destination)
      rider.request_time = request_time

      # Schedule Rider Event
      self.schedule_event(rider.request_time, "RIDER_REQUEST", rider)
      # Add to rider dictionary for future reference
      self.riders[rider.id] = rider

      # Generate a new request time for the next rider
      request_time += math.floor(random.expovariate(1 / MEAN_ARRIVAL_TIME))
      # Increment num for next rider generation id
      self.rider_id_num += 1
      # Decrement number of riders to generate
      current_num_riders += 1
    
  def calculate_travel_time(self, start_location: tuple, end_location: tuple) -> float:
    """Calculates the Manhattan Distance then returns the travel time"""
    x1, y1 = start_location
    x2, y2 = end_location
    distance = abs(x1 - x2) + abs(y1 - y2)
    travel_time = distance * TRAVEL_SPEED_FACTOR
    return travel_time

  def find_closest_car_brute_force(self, rider_location: tuple) -> Car:
    """Returns the closest Car"""
    shortest_distance = math.inf
    car = None

    for car in self.cars.values():
      # Ensure car's status is available before attempting to calculate
      if car.status != "available":
        continue
      distance = self.calculate_travel_time(car.location, rider_location)
      print(f"{car.id} distance to {rider_location} -> {distance}")
      if distance < shortest_distance:
        shortest_distance = distance
        closest_car = car
    print(f"\n...Selected: {closest_car.id}\n")

    return closest_car

  # --- EVENT HANDLERS ---

  # Schedule
  def schedule_event(self, timestamp: int, event_type: str, data: Rider | Car) -> None:
    """Adds an event to the event queue."""
    heapq.heappush(
      self.event_queue, 
      Event(
        timestamp,
        next(self.sequence_number),
        event_type,
        data
      )
    )

  # Rider request
  def handle_rider_request(
      self, 
      rider: Rider 
    ) -> None:
      print(
        f"RIDER_REQUEST: time={self.current_time},"
        f"rider={rider.id}"
      )
      # Convert rider start tuple into a Point to query
      query_point = Point(rider.start_location[0], rider.start_location[1])
      candidate_points = (
        self.available_car_quadtree.root.find_k_nearest(
          query_point,
          k=self.candidate_count
        )
      )
      rider_vertex: Point = self.map.find_nearest_vertex(rider.start_location)
      best_route: list[str] | None = None
      best_pickup_time = math.inf
      best_car: Car | None = None

      # Evaluate the best candidate 
      for candidate in candidate_points:
        car: Car = candidate.data
        car_vertex = self.map.find_nearest_vertex(car.location)
        path, time = find_shortest_path(self.map, car_vertex, rider_vertex)
        if path is None:
          continue
        if time < best_pickup_time:
          best_pickup_time = time
          best_route = path
          best_car = car

      if best_route is None:
        # FIXME: add to waiting dict
        print(f"REPORT: generate_rider_request({rider.id}) car match unsuccessful...")

      if best_car is not None:
        self.remove_available_car(best_car)
        
        best_car.status = "en_route_to_pickup"
        best_car.assigned_rider = rider
        best_car.route = best_route
        best_car.route_time = best_pickup_time
        best_car.busy_start_time = self.current_time
        rider.status = "waiting"

        self.schedule_event(self.current_time + best_car.route_time, "PICKUP_ARRIVAL", best_car)
        print(f"TIME {self.current_time}: CAR {car.id} dispatched to RIDER {rider.id}")

  # Pickup
  def handle_pickup_arrival(self, car: Car) -> None:
    rider: Rider = car.assigned_rider

    print(
      f"PICKUP_ARRIVAL: time={self.current_time},"
      f"car={car.id},"
      f"assigned_rider={rider}"
    )

    # Update car location, car status, and rider status
    car.location = rider.start_location
    car.status = "en_route_to_destination"
    rider.status = "in_car"
    rider.pickup_time = self.current_time
    rider_wait_time = rider.pickup_time - rider.request_time
    # Create points to use in dijkstra's algorithm
    car_vertex = self.map.find_nearest_vertex(car.location)
    destination_vertex = self.map.find_nearest_vertex(rider.destination)
    path, time = find_shortest_path(self.map, car_vertex, destination_vertex)

    # If a path exists to destination...
    if path is not None:
      car.route = path
      self.schedule_event(self.current_time + time, "DROPOFF_ARRIVAL", car)
    # Else remove the rider from the car, note the unsuccessful trip, and make the care available
    else:
      print(f"{rider.id} trip is unsuccessful.")
      car.total_busy_time = rider_wait_time
      car.assigned_rider = None
      self.add_available_car(car)

  # Dropoff
  def handle_dropoff_arrival(self, car: Car) -> None:
    print(
      f"DROPOFF: time={self.current_time},"
      f"car={car.id},"
      f"assigned_rider={car.assigned_rider}"
    )
    # car: Car = event.data
    rider: Rider = car.assigned_rider
    
    print(f"TIME {self.current_time}: CAR {car.id} dropped off RIDER {rider.id}")

    # Update car location, car status, and rider status
    car.location = rider.destination
    rider.status = "completed"
    rider.dropoff_time = self.current_time
    car.assigned_rider = None

    car.total_busy_time += (self.current_time - car.busy_start_time)
    car.trips_completed += 1
    self.add_available_car(car)

  # --- EVENT LOOP ---

  def run(self) -> None:
    """Runs the simulation by processing events in the event queue."""
    print("--- Starting Simulation ---\n")
    while self.event_queue:
      event = heapq.heappop(self.event_queue)
      # Advance the simulation clock
      self.current_time = event.timestamp

      print(
        f"EVENT: time={event.timestamp},"
        f"type={event.event_type},"
        f"data={event.data}"
      )

      if event.event_type == "RIDER_REQUEST":
        self.handle_rider_request(event.data)

      elif event.event_type == "PICKUP_ARRIVAL":
        self.handle_pickup_arrival(event.data)

      elif event.event_type == "DROPOFF_ARRIVAL":
        self.handle_dropoff_arrival(event.data)

      else: 
        raise ValueError(f"Unknown event type: {event.event_type}")

    print(f"\n--- Simulation Complete (sim time: {self.current_time}) ---")

  def __str__(self):
    return (f"""
--- Simulation Attributes ---

Cars: {self.cars}

Riders: {self.riders}
{self.map}
-----------------------------
""")  

def main():
  parser = argparse.ArgumentParser(description="Arguments can be passed in the CLI to adjust simulation.")
  parser.add_argument("--max-time", type=int, default=DEFAULT_MAX_TIME, help="Set the max time for the simulation.")
  parser.add_argument("--num-riders", type=int, default=5, help="Set the number of riders.")
  parser.add_argument("--map-file", type=str, default=DEFAULT_MAP, help="Set the map file.")
  
  return parser.parse_args()

if __name__ == "__main__":
  args = main()
  simulation = Simulation(
    map_filename=args.map_file,
    max_time=args.max_time,
    num_riders=args.num_riders
  )

  print(f"x: {simulation.boundary.x}")
  print(f"y: {simulation.boundary.y}")
  print(f"width: {simulation.boundary.width}")
  print(f"height: {simulation.boundary.height}")

  simulation.generate_cars()
  simulation.generate_rider_request()

  print(f"Number of cars: {len(simulation.cars)}")
  print(f"Number of riders: {simulation.riders}")

  simulation.run()
