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
DEFAULT_MAP: str = 'Final_Map_50_Node_Grid.csv'
DEFAULT_MAX_TIME: int = 20
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
  def __init__(self, map_filename):
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
    
    # Default settings
    self.car_id_num: int = 1
    self.rider_id_num: int = 1
    self.num_cars: int = 5
    self.num_riders: int = 5
    self.max_time: int = DEFAULT_MAX_TIME
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
        self.available_cars[car.id] = Car
        self.available_car_points[car.id] = car_point
        car.status = "available"
      else: 
        print(f"REPORT: add_available_car({car.id}) unsuccessful...")

  def remove_available_car(self, car: Car) -> None:
    car_point_to_remove = self.available_car_points[car.id]
    is_successful = self.available_car_quadtree.root.remove(car_point_to_remove)
    # If removed from quadtree successfully, pop from available car points
    if is_successful:
      self.available_car_points.pop(car.id, None)
    else: 
      print(f"REPORT: remove_available_car({car.id}) unsuccessful...")

  def generate_rider_request(self):
    request_time = self.current_time # Begins at initial value of 0
    while self.num_riders > 0:
      # If max time is not exceeded, generate riders
      if request_time < self.max_time:
        # Generate a Rider
        rider_id = "Rider-" + str(self.rider_id_num)
        x_min = self.boundary.x
        y_min = self.boundary.y
        x_max = self.boundary.width
        y_max = self.boundary.height
        start = (random.uniform(x_min, x_max), random.uniform(y_min, y_max))
        destination = (random.uniform(x_min, x_max), random.uniform(y_min, y_max))
        rider = Rider(rider_id, start, destination)
        rider.request_time = request_time
        # Schedule Rider Event
        self.schedule_event(rider.request_time, "RIDER_REQUEST", rider)
        # Convert rider start tuple into a Point to query
        query_point = Point(start[0], start[1])
        candidate_points = (
          self.available_car_quadtree.root.find_k_nearest(
            query_point,
            k=self.candidate_count
          )
        )
        # Generate a new request time for the next rider
        request_time += math.floor(random.expovariate(1 / MEAN_ARRIVAL_TIME))
        # Increment num for next rider generation id
        self.rider_id_num += 1
        # Decrement number of riders to generate
        self.num_riders -= 1
      else:
        print(f"Time is up!")
        break
    
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
  def handle_rider_request(self, rider: Rider) -> None:
    print(f"Matching rider {rider.id} with a driver...\n")
    # Find closest available car and assign it to the rider
    car = self.find_closest_car_brute_force(rider.start_location)
    # Link the rider to this car and update car's status
    car.assigned_rider = rider
    car.status = "en_route_to_pickup"
    # Calculate time from car to rider
    pickup_duration = self.calculate_travel_time(car.location, rider.start_location)

    self.schedule_event(self.current_time + pickup_duration, "PICKUP_ARRIVAL", car)
    print(f"TIME {self.current_time}: CAR {car.id} dispatched to RIDER {rider.id}")

  # Pickup
  def handle_pickup_arrival(self, car: Car) -> None:
    # car: Car = event.data
    rider: Rider = car.assigned_rider

    print(f"TIME {self.current_time}: CAR {car.id} picked up RIDER {rider.id}")

    # Update car location, car status, and rider status
    car.location = rider.start_location
    car.status = "en_route_to_destination"
    rider.status = "in_car"
    # Calculate time from rider to destination
    dropoff_duration = self.calculate_travel_time(car.location, rider.destination)

    self.schedule_event(self.current_time + dropoff_duration, "DROPOFF_ARRIVAL", car)
    #print(f"TIME {self.current_time}: CAR {car.id} dispatched to RIDER {rider.id}")

  # Dropoff
  def handle_dropoff_arrival(self, car: Car) -> None:
    # car: Car = event.data
    rider: Rider = car.assigned_rider

    print(f"TIME {self.current_time}: CAR {car.id} dropped off RIDER {rider.id}")

    # Update car location, car status, and rider status
    car.location = rider.destination
    car.status = "available"
    rider.status = "completed"
    car.assigned_rider = None

  # --- EVENT LOOP ---

  def run(self) -> None:
    """Runs the simulation by processing events in the event queue."""
    print("--- Starting Simulation ---\n")
    while self.event_queue:
      event = heapq.heappop(self.event_queue)
      # Advance the simulation clock
      self.current_time = event.timestamp

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
  parser.add_argument("--max-time", type=int, default=100, help="Set the max time for the simulation.")
  parser.add_argument("--num-riders", type=int, default=5, help="Default riders set to 5.")
  parser.add_argument("--map-file", type=str, default='map.csv', help="Default map setting.")
  # parser.add_argument("--num-cars", type=int, default=5, help="Default number of cars set to _.")
  # parser.add_argument("--candidate-count", type=int, default=5, help="Default candidate count set to _.")
  # parser.add_argument("--random-seed", type=int, default=5, help="Default seed set to _.")
  args = parser.parse_args()

  if args.max_time:
    print(f"Max-time set to: {args.max_time}")
  if args.num_riders:
    print(f"Num-riders set to: {args.num_riders}")
  if args.map_file:
    # DEFAULT_MAP = args.map_file
    print(f"Map set to: {args.map_file}")

if __name__ == "__main__":
  main()
  simulation = Simulation(DEFAULT_MAP)
  # print(simulation.map)
  print(f"x: {simulation.boundary.x}")
  print(f"y: {simulation.boundary.y}")
  print(f"width: {simulation.boundary.width}")
  print(f"height: {simulation.boundary.height}")

  simulation.generate_cars()
  #simulation.generate_rider_request()
  print(simulation.cars)
  print(simulation.available_car_points)
  # print(simulation.event_queue)
  # print(len(simulation.event_queue))

  path, distance = find_shortest_path(simulation.map, 'N1', 'N19')
  print(path)
  print(distance)

  # simulation.cars["car1"] = Car("CAR001", (10.0, 5.0))
  # simulation.cars["car2"] = Car("CAR002", (15.0, 20.0))

  # rider1 = Rider("RIDER001", (20.0, 5.0), (10.0, 10.0))
  # rider2 = Rider("RIDER002", (20.0, 20.0), (10.0, 10.0))

  # simulation.schedule_event(timestamp=5, event_type="RIDER_REQUEST", data=rider1)
  # simulation.schedule_event(timestamp=10, event_type="RIDER_REQUEST", data=rider2)

  # car1.calculate_route('C', simulation.map.adjacency_list)
  # car2.calculate_route('C', simulation.map.adjacency_list)

  #simulation.run()

