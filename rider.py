class Rider:
  def __init__(self, rider_id: str, pickup_loc: tuple, dropoff_loc: tuple):
    self.id: str = rider_id
    self.start_location: tuple = pickup_loc
    self.destination: tuple = dropoff_loc
    self.status: str = "waiting" # -> "in_car" -> "completed"
    self.request_time: int | None = None
    self.pickup_time: int | None = None
    self.dropoff_time: int | None = None

  def __str__(self):
    return f"\nRider {self.id} at {self.start_location} {self.status} for ride to {self.destination}."
