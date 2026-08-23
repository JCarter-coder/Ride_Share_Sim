import pytest
from rider import Rider

@pytest.fixture
def create_rider():
  rider = Rider("Rider001", (4.000, 2.200), (1.333, 1.110))
  return rider

def test_rider_initialization(create_rider):
  rider = create_rider
  assert rider.id == "Rider001"
  assert rider.start_location == (4.000, 2.200)
  assert rider.destination == (1.333, 1.110)
  assert rider.status == "waiting"
  assert rider.request_time == None
  assert rider.pickup_time == None
  assert rider.dropoff_time == None

def test_rider_str(create_rider):
  rider = create_rider
  expected_str = f"\nRider {rider.id} at {rider.start_location} {rider.status} for ride to {rider.destination}."
  assert str(rider) == expected_str