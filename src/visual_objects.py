from math import sqrt
from math import atan, pi, sin, cos, degrees
import sys
eps = 10e-5


def is_closer(first: 'Edge', second: 'Edge', ray: 'Ray'):
    intersection1 = ray.intersect(first)
    intersection2 = ray.intersect(second)

    if not intersection1 or not intersection2:
        raise ValueError("Can't find closer edge")

    if intersection1 == intersection2:
        first_other = first.get_other(intersection1)
        second_other = second.get_other(intersection1)
        r = Ray(intersection1, first_other)
        e = Edge(ray.start, second_other)

        return r.intersect(e) is not None

    return ray.start.dist(intersection1) < ray.start.dist(intersection2)

def move(point, target):
    return Point(point.x - target.x, point.y - target.y)

def polar_angle(point):
    angle = (pi / 2) if point.x == 0.0 else atan(abs(point.y) / abs(point.x))
    if point.x <= 0 and point.y > 0:
        angle = pi - angle
    elif point.x < 0 and point.y <= 0:
        angle += pi
    elif point.x >= 0 and point.y < 0:
        angle = 2 * pi - angle
    return angle


def rotate(point, angle):
    x = point.x * cos(angle) - point.y * sin(angle)
    y = point.x * sin(angle) + point.y * cos(angle)
    return Point(x, y)


def get_angle(a, b, c):
    b = move(b, a)
    c = move(c, a)
    return polar_angle(rotate(c, -polar_angle(b)))

def det2(a, b, c, d):
    return a * d - b * c


def elipse_box(p, d=4):
    x, y = p
    return [(x - d, y - d), (x + d, y + d)]


class Point:
    def __init__(self, x: float, y: float):
        self.x, self.y = x, y
        self.edges = set()

    def add_edge(self, edge: 'Edge'):
        if len(self.edges) == 2: 
            raise ValueError("Strange situation, becouse vertex can have only two points")
        self.edges.add(edge)

    @property
    def coordinates(self):
        return (self.x, self.y)

    def dist(self, other: 'Point') -> float:
        if not other:
            return 0
        return  sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return abs(self.x - other.x) <= eps and abs(self.y - other.y) <= eps

    def __str__(self):
        return f"({self.x},{self.y})"
    
    def __repr__(self):
        return str(self)


class Edge:
    def __init__(self, a: Point, b: Point, visible: bool = True):
        self.a, self.b = a, b
        self.visible = visible

    @staticmethod
    def median(a: Point, b: Point):
        return Point((a.x + b.x) / 2, (a.y + b.y) / 2)

    def contains(self, point: Point):
        a, b = self.a, self.b
        # todo: epsilon for equals
        return ((   max(a.x, b.x) >= point.x 
                and min(a.x, b.x) <= point.x
                and max(a.y, b.y) >= point.y 
                and min(a.y, b.y) <= point.y) 
            or ((a == point) or (b == point)))

    def __repr__(self):
        return str(self)    

    def get_points(self):
        return {self.a, self.b}

    def get_other(self, other):
        return self.b if other == self.a else self.a

    def __str__(self):
        return f"Edge[{self.a}, {self.b}]"

    def __hash__(self):
        return hash((self.a.x, self.a.y, self.b.x, self.b.y))

    def __eq__(self, other):
        return self.a == other.a and self.b == other.b

    def intersect(self, edge: 'Edge'):
        a, b = self.a, self.b
        first = Ray(a, b).intersect(edge)
        second = Ray(b, a).intersect(edge)
        if first is not None and second is not None:
            return first
        return None

class Ray:
    def __init__(self, start: Point, end: Point):
        self.start, self.end = start, end

    def contains(self, point: Point):
        max_dist = max(self.start.dist(point), self.start.dist(self.end))
        between = point.dist(self.end)
        return max_dist >= between

    def intersect(self, edge: Edge):
        x1, y1 = self.start.coordinates
        x2, y2 = self.end.coordinates
        x3, y3 = edge.a.coordinates
        x4, y4 = edge.b.coordinates
        d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if d == 0: 
            return None
        x = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / d
        y = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / d
        p = Point(x, y)
        
        if (not edge.contains(p)) or (not self.contains(p)):
            return None
        return p
        
    def intersect_dist(self, edge: Edge):
        if not self.intersect(edge):
            raise ValueError("No intersections")
        return self.start.dist(self.intersect(edge))

class Polygon:
    def __init__(self, points: [Point], visible=True):
        self.points = points
        self.visible = visible
        for edge in self.edges:
            edge.a.add_edge(edge)
            edge.b.add_edge(edge)

    @property
    def edges(self):
        if len(self.points) == 2:
            return [Edge(self.points[0], self.points[1], visible=self.visible)]
        result = []
        first = self.points[0]
        for point in self.points[1:]:
            result.append(Edge(first, point, visible=self.visible))
            first = point
        result.append(Edge(first, self.points[0], visible=self.visible))
        return result


if __name__ == "__main__":
    ray = Ray(
        start=Point(194, 247),
        end=Point(281, 501)
    )

    edge = Edge(
        a=Point(281, 501),
        b=Point(372.69, 414.43)
    )
    print(ray.intersect(edge))
    
