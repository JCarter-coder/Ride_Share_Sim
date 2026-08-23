import argparse
import heapq
import math
from dataclasses import dataclass, field
from enum import Enum, auto
# from typing import Any
from itertools import count
from car import Car
from rider import Rider
from graph import Graph
from pathfinding import find_shortest_path

# Global settings
TRAVEL_SPEED_FACTOR = 1
DEFAULT_MAP: str = 'map.csv'
DEFAULT_CANDIDATE_COUNT = 5

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
    self.cars = {}
    self.riders = {}
    self.map = Graph()

    self.map.load_map_data(map_filename)

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
  simulation = Simulation('Final_Map_50_Node_Grid.csv')
  print(simulation.map)

  path, distance = find_shortest_path(simulation.map, 'N1', 'N19')
  print(path)
  print(distance)

  simulation.cars["car1"] = Car("CAR001", (10.0, 5.0))
  simulation.cars["car2"] = Car("CAR002", (15.0, 20.0))

  rider1 = Rider("RIDER001", (20.0, 5.0), (10.0, 10.0))
  rider2 = Rider("RIDER002", (20.0, 20.0), (10.0, 10.0))

  simulation.schedule_event(timestamp=5, event_type="RIDER_REQUEST", data=rider1)
  simulation.schedule_event(timestamp=10, event_type="RIDER_REQUEST", data=rider2)

  # car1.calculate_route('C', simulation.map.adjacency_list)
  # car2.calculate_route('C', simulation.map.adjacency_list)

  simulation.run()

