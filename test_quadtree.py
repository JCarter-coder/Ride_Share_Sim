import pytest
import random
from quadtree import Quadtree, QuadtreeNode, Point, Rectangle

@pytest.fixture
# Create a quadtree with a boundary of 1000 x 1000 for testing
def create_quadtree():
  # Arrange
  boundary = Rectangle(0, 0, 1000, 1000)
  qt = Quadtree(boundary)
  return qt

@pytest.fixture
# Create a list of random points for testing
def create_random_points():
  # Arrange
  num_points = 5000
  points = [
    Point(random.uniform(0, 1000), random.uniform(0, 1000), data=f"Point {i}") 
    for i in range(num_points)
  ]
  return points

def test_list_points(create_random_points):
  # Act
  points = create_random_points

  # Assert list of Points
  assert isinstance(points, list) and all(isinstance(x, Point) for x in points), "'points' is not a list of Point objects"

def test_quadtree(create_quadtree):
  # Act
  qt = create_quadtree

  # Assert quadtree root is a QuadtreeNode
  assert type(qt) == Quadtree, "Quadtree is not a Quadtree object"
  assert type(qt.root) == QuadtreeNode, "Quadtree root is not a QuadtreeNode"

def test_find_nearest(create_quadtree, create_random_points):
  # Arrange
  query_point = Point(random.uniform(0, 1000), random.uniform(0, 1000), data="Query Point")

  # Act
  qt = create_quadtree
  points = create_random_points

  # Insert points into the quadtree
  for p in points:
    qt.root.insert(p)

  # Quadtree search for the nearest point using O(log N) algorithm
  best_found_qt = {'point': None, 'dist_sq': float('inf')}
  qt.root.find_nearest(query_point, best_found_qt)

  # Brute force search for the nearest point using O(N) algorithm
  best_point_bf = None
  best_dist_sq_bf = float('inf')
  for p in points:
    dist_sq = (p.x - query_point.x)**2 + (p.y - query_point.y)**2
    if dist_sq < best_dist_sq_bf:
      best_dist_sq_bf = dist_sq
      best_point_bf = p

  # Output the results for debugging
  print(f"Quadtree nearest point: {best_found_qt['point'].data}")
  print(f"Quadtree nearest distance squared: {best_found_qt['dist_sq']}\n")
  print(f"Brute Force nearest point: {best_point_bf.data}")
  print(f"Brute Force nearest distance squared: {best_dist_sq_bf}\n")

  assert best_found_qt['point'] == best_point_bf, "Quadtree nearest point doesn't match brute force nearest point"
  assert best_found_qt['dist_sq'] == best_dist_sq_bf, "Quadtree nearest distance doesn't match brute force nearest distance"
