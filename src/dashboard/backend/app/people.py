import random
from shapely.geometry import Polygon, Point
import time

"""Bounded area coordinates"""
AREA1_NW_BOUND = [25.652304, -100.287249]
AREA1_NE_BOUND = [25.652404, -100.286949]
AREA1_SW_BOUND = [25.652, -100.287249]
AREA1_SE_BOUND = [25.652104, -100.286949]
AREA2_NW_BOUND = [25.652704, -100.286049]
AREA2_NE_BOUND = [25.652894, -100.285649]
AREA2_SW_BOUND = [25.652494, -100.286049]
AREA2_SE_BOUND = [25.652614, -100.285659]


def random_timestamp_ms():
    """Returns a random timestamp in milliseconds."""
    timestamp = time.time()
    ms = random.randint(0, 999)
    timestamp_ms = int(timestamp * 1000) + ms
    return timestamp_ms

def random_coordinate_within_shape(c1, c2, c3, c4):
    """Get a random coordinate inside of a defined polygon"""
    lat1, lng1 = c1
    lat2, lng2 = c2
    lat3, lng3 = c3
    lat4, lng4 = c4
    poly = Polygon([(lat1,lng1), (lat2,lng2),(lat3,lng3), (lat4,lng4)])
    min_x, min_y, max_x, max_y = poly.bounds
    
    while True:
      random_point = Point([random.uniform(min_x, max_x), random.uniform(min_y, max_y)])
      if (random_point.within(poly)):
          return random_point

def gen_people_points():
    """Create random people entities"""
    points = []
    for i in range(10):
        p = random_coordinate_within_shape(AREA1_NW_BOUND, AREA1_NE_BOUND, AREA1_SE_BOUND, AREA1_SW_BOUND)
        ts = random.randint(1684562400000, 1685734341242)
        points.append({"lat": p.x, "lon": p.y, "taken_at": ts})
    for i in range(10):
        p = random_coordinate_within_shape(AREA2_NW_BOUND, AREA2_NE_BOUND, AREA2_SE_BOUND, AREA2_SW_BOUND)
        ts = random.randint(1684562400000, 1685734341242)
        points.append({"lat": p.x, "lon": p.y, "taken_at": ts})
    return points