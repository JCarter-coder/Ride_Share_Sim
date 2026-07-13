from car import Car
from rider import Rider

class Simulation:
  def __init__(self):
    self.cars = {}
    self.riders = {}

  def __str__(self):
    return (f"""
----Simulation Attributes----
Cars: {self.cars}

Riders: {self.riders}
-----------------------------
""")
  

simulation = Simulation()
print(simulation)

simulation.cars["CAR001"] = Car("CAR001", (10, 5))
simulation.cars["CAR002"] = Car("CAR002", (5, 6))

simulation.riders["RIDER_A"] = Rider("RIDER_A", (1, 2), (20, 15))
simulation.riders["RIDER_B"] = Rider("RIDER_B", (10, 12), (2, 1))

print(simulation)
print(simulation.cars.get("CAR001"))
print(simulation.cars.get("CAR002"))
print(simulation.riders.get("RIDER_A"))
print(simulation.riders.get("RIDER_B"))
print(simulation.riders.get("RIDER_C"))
