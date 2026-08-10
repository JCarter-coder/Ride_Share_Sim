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
    self.points = []
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

class Quadtree:
  """A quadtree data structure for efficient spatial queries."""
  def __init__(self, boundary: Rectangle):
    self.root = QuadtreeNode(boundary)