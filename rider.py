class Rider:
  def __init__(self, rider_id, pickup_loc, dropoff_loc):
    self.id = rider_id
    self.start_location = pickup_loc
    self.destination = dropoff_loc
    self.status = "waiting" # in_car, completed

  def __str__(self):
    return f"\nRider {self.id} at {self.start_location} {self.status} for ride to {self.destination}."
  
# rider1 = Rider("RIDER_A", (1, 2), (20, 15))
# rider2 = Rider("RIDER_B", (10, 12), (2, 1))

# print(rider1)
# print(rider2)