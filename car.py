class Car:
  def __init__(self, id, initial_location):
    self.id = id # string
    self.location = initial_location # tuple (x, y)
    self.status = "available" # en_route_to_pickup, en_route_to_destination, unavailable
    self.destination = None

  def __str__(self):
    return f"\nCar {self.id} at {self.location} - Status: {self.status}."

# car1 = Car("CAR001", (10, 5))
# car2 = Car("CAR002", (5, 6))

# print(car1)
# print(car2)