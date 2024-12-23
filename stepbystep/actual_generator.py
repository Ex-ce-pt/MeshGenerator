"""File with functions responsible for heavy-lifting."""

import math

class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'({self.x} ; {self.y})'

####################################
# Input parameters

PROXIMITY_RADIUS: float = 1e-09
HOLE_RADIUS: float = 0.1
HOLE_CENTERS: list[Point] = [
    Point(0.5, 0.5),
    Point(0.3, 0.25),
    Point(0.8, 0.8),
    Point(0.2, 0.85)
]
NUMBER_OF_VERTICES: int = 50

####################################

def compute_polygons() -> list[list[Point]]:
    polygons: list[list[Point]] = []

    for hole_center in HOLE_CENTERS:
        polygon: list[Point] = [Point(hole_center.x + HOLE_RADIUS, hole_center.y)]

        for vertex_index in range(1, NUMBER_OF_VERTICES):
            angle = vertex_index * 2 * math.pi / NUMBER_OF_VERTICES
            new_vertex = Point(hole_center.x + HOLE_RADIUS * math.cos(angle), hole_center.y + HOLE_RADIUS * math.sin(angle))
            polygon.append(new_vertex)

        polygons.append(polygon)

    return polygons


def segments_intersect(a: Point, b: Point, c: Point, d: Point, ignore_endpoint_proximity=False) -> bool:
    # https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
    denominator = (a.x - b.x) * (c.y - d.y) - (a.y - b.y) * (c.x - d.x)
    if denominator == 0: # The lines are parallel
        return False

    intersection = (
        ((a.x * b.y - a.y * b.x) * (c.x - d.x) - (a.x - b.x) * (c.x * d.y - c.y * d.x)) / denominator,
        ((a.x * b.y - a.y * b.x) * (c.y - d.y) - (a.y - b.y) * (c.x * d.y - c.y * d.x)) / denominator
    )

    # my own genius from this point on
    # compute vectors (ab), (ap), (cd), (cp), where p is the intersection point
    # (ab) || (ap) & (cd) || (cp)
    # (ap) = m * (ab) ; if m <= 1 ==> p belongs to (ab) }
    # (cp) = n * (cd) ; if n <= 1 ==> p belongs to (cd) } => count the intersection

    ab_vec = (b.x - a.x, b.y - a.y)
    ap_vec = (intersection[0] - a.x, intersection[1] - a.y)
    m = ap_vec[0] / ab_vec[0] if not math.isclose(ab_vec[0], 0, abs_tol=PROXIMITY_RADIUS) else ap_vec[1] / ab_vec[1]
    cd_vec = (d.x - c.x, d.y - c.y)
    cp_vec = (intersection[0] - c.x, intersection[1] - c.y)
    n = cp_vec[0] / cd_vec[0] if not math.isclose(cd_vec[0], 0, abs_tol=PROXIMITY_RADIUS) else cp_vec[1] / cd_vec[1]

    intersection_close_to_endpoints = any(math.isclose(coefficient, value, abs_tol=PROXIMITY_RADIUS) for coefficient in (m, n) for value in (0, 1))
    if 0 < m <= 1 and 0 < n <= 1 and (not ignore_endpoint_proximity or not intersection_close_to_endpoints):
        return True
        # Code below replaced by the 3rd condition of the if statement above.
        # if not ignore_endpoint_proximity:
        #     return True
        #
        # if ignore_endpoint_proximity and not intersection_close_to_endpoints:
        #     return True

    return False

def segment_intersects_any(points: list[Point], connections: dict[int, set[int]], a_idx: int, b_idx: int) -> bool:
    for c_idx in range(len(points)):
        for d_idx in connections[c_idx]:
            # If there exists the connection c <-> d, then there also exists d <-> c
            # If d_idx is less than c_idx, such connection has already been handled since the loop got to d_idx first
            if d_idx < c_idx:
                continue

            # The segments share at least one endpoint, obviously do intersect
            if a_idx == c_idx or a_idx == d_idx or b_idx == c_idx or b_idx == d_idx:
                continue

            if segments_intersect(points[a_idx], points[b_idx], points[c_idx], points[d_idx]):
                return True
    return False

####################################

if __name__ == '__main__':
    print("RUN MESH_GENERATOR.PY, YOU DUMBASS!!! FFS...")
