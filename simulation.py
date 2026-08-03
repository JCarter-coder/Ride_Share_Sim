from car import Car
from rider import Rider
from graph import Graph

class Simulation:
  def __init__(self, map_filename):
    self.cars = {}
    self.riders = {}
    self.map = Graph()

    self.map.load_from_file(map_filename)

  def __str__(self):
    return (f"""
--- Simulation Attributes ---

Cars: {self.cars}

Riders: {self.riders}
{self.map}
-----------------------------
""")  

if __name__ == "__main__":
  simulation = Simulation('map.csv')

  car1 = Car("CAR001", 'A')
  car2 = Car("CAR002", 'B')

  print(simulation)

  car1.calculate_route('C', simulation.map.adjacency_list)
  car2.calculate_route('C', simulation.map.adjacency_list)

  print(car1)
  print(car2)

