import heapq
import itertools

class Point:
  """A point in 2D space with an optional data attribute, e.g. label/identifier."""
  def __init__(self, x, y, data=None):
    self.x = x
    self.y = y
    self.data = data # Optional info for this point

  def __repr__(self):
    return f"Point({self.x:.6f}, {self.y:.6f}, data={self.data})"

class Rectangle:
  """This is the boundary of a quadtree node defined by 
  the top-left corner and its width and height."""
  def __init__(self, x, y, width, height):
    self.x = x
    self.y = y
    self.width = width
    self.height = height

  def contains(self, point: Point) -> bool:
    return (self.x <= point.x < self.x + self.width and
            self.y <= point.y < self.y + self.height)

  def distance_sq_to_point(self, point: Point) -> float:
    dx = max(0, self.x - point.x, point.x - (self.x + self.width))
    dy = max(0, self.y - point.y, point.y - (self.y + self.height))
    return dx * dx + dy * dy

class QuadtreeNode:
  """A node in the quadtree that can contain points and subdivide into four child nodes."""
  def __init__(self, boundary: Rectangle, capacity=4):
    self.boundary = boundary
    self.points: list[Point] = []
    self.capacity = capacity
    self.divided = False
    # Children nodes
    self.northwest = None
    self.northeast = None
    self.southwest = None
    self.southeast = None

  def subdivide(self) -> None:
    """Divide this node into four child nodes."""
    x, y, w, h = self.boundary.x, self.boundary.y, self.boundary.width, self.boundary.height

    nw_boundary = Rectangle(x, y, w/2, h/2)
    self.northwest = QuadtreeNode(nw_boundary, self.capacity)

    ne_boundary = Rectangle(x + w/2, y, w/2, h/2)
    self.northeast = QuadtreeNode(ne_boundary, self.capacity)

    sw_boundary = Rectangle(x, y + h/2, w/2, h/2)
    self.southwest = QuadtreeNode(sw_boundary, self.capacity)

    se_boundary = Rectangle(x + w/2, y + h/2, w/2, h/2)
    self.southeast = QuadtreeNode(se_boundary, self.capacity)

    self.divided = True

    for p in self.points:
      self.insert(p)
    self.points = []

  def insert(self, point: Point) -> bool:
    # If point is outside the boundary, do nothing
    if not self.boundary.contains(point):
      return False
    
    # If the node has capacity, and the node is not divided, add the point to this node
    if len(self.points) < self.capacity and not self.divided:
      self.points.append(point)
      return True
    
    # If the node is full, subdivide and insert into applicable child node
    if not self.divided:
      self.subdivide()

    if self.northwest.insert(point): return True
    if self.northeast.insert(point): return True
    if self.southwest.insert(point): return True
    if self.southeast.insert(point): return True

    return False # Should not reach here if code executed correctly

  def find_nearest(self, point: Point, best_found):
    # Prune nodes that are further than best found distance
    if self.boundary.distance_sq_to_point(point) > best_found['dist_sq']:
      return

    # Check points within this node
    for p in self.points:
      dist_sq = (p.x - point.x)**2 + (p.y - point.y)**2
      if dist_sq < best_found['dist_sq']:
        best_found['dist_sq'] = dist_sq
        best_found['point'] = p

    # Recursively check child nodes if they exist
    if self.divided:
      children = [self.northwest, self.northeast, self.southwest, self.southeast]
      children.sort(key=lambda child: child.boundary.distance_sq_to_point(point))

      for child in children:
        child.find_nearest(point, best_found)

    return

  def find_k_nearest(self, query_point: Point, k: int = 5) -> list[Point]:
    # Reject nonpositive k values
    if k <= 0:
      raise ValueError("k must be a positive integer.")

    candidates: list[Point] = []
    counter: int = itertools.count()

    self._find_k_nearest(query_point, k, candidates, counter)

    # Convert to nearest to farthest order
    results = sorted(
      candidates,
      key=lambda candidate: -candidate[0]
    )

    return [candidate[2] for candidate in results]
  
  # Internal method
  def _find_k_nearest(self, query_point: Point, k: int, candidates: list[Point], counter: int) -> None:
    if len(candidates) == k:
      farthest_dist_sq = -candidates[0][0]

      if self.boundary.distance_sq_to_point(query_point) > farthest_dist_sq:
        return

    for point in self.points:
      dist_sq = (
        (point.x - query_point.x)**2 +
        (point.y - query_point.y)**2
      )

      candidate = (-dist_sq, next(counter), point)

      if len(candidates) < k:
        heapq.heappush(candidates, candidate)

      else:
        farthest_dist_sq = - candidates[0][0]

        if dist_sq < farthest_dist_sq:
          heapq.heapreplace(candidates, candidate)

    # Recursively search children nodes
    if self.divided:
      children = [
        self.northwest,
        self.northeast,
        self.southwest,
        self.southeast
      ]

      children.sort(
        key=lambda child: child.boundary.distance_sq_to_point(query_point)
      )

      for child in children:
        child._find_k_nearest(query_point, k, candidates, counter)

  def remove(self, point: Point) -> bool:
    if not self.boundary.contains(point):
      return False

    for index, stored_point in enumerate(self.points):
      # Ensure point is explicitly described (not just by coordinates)
      if stored_point is point:
        self.points.pop(index)
        return True

    if self.divided:
      children = [
        self.northwest,
        self.northeast,
        self.southwest,
        self.southeast
      ]

      for child in children:
        if child.bouadary.contains(point):
          if child.remove(point):
            return True

    return False

class Quadtree:
  """A quadtree data structure for efficient spatial queries."""
  def __init__(self, boundary: Rectangle):
    self.root = QuadtreeNode(boundary)