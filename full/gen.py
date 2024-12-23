"""Actual generator. Can be considered one big function."""

import math

class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'({self.x} ; {self.y})'

class Graph:
    def __init__(self):
        self.points: list[Point] = []
        self.connections: dict[int, set[int]] = dict() # The ints are the indices of points from the previous list


####################################

PROXIMITY_RADIUS: float = 1e-09

# Saves the polygon data
def save_polygon_elements(graph: Graph, polygons_list: list[list[int]], polygon: list[Point]) -> None:
    num_vertices = len(polygon)
    first_vertex_id = len(graph.points)

    # Register all the vertices of the polygon
    graph.points.extend(polygon)

    # Save polygon points indices for Stage 4
    polygons_list.append([first_vertex_id + v for v in range(num_vertices)])

    for begin_vertex_index in range(num_vertices):
        # Get IDs (indices in the points list)
        begin_vertex_id = first_vertex_id + begin_vertex_index
        end_vertex_index = (begin_vertex_index + 1) % num_vertices
        end_vertex_id = first_vertex_id + end_vertex_index

        # Initialize the sets, if the keys are not yet present
        graph.connections.setdefault(begin_vertex_id, set())
        graph.connections.setdefault(end_vertex_id, set())

        # Connect together
        graph.connections[begin_vertex_id].add(end_vertex_id)
        graph.connections[end_vertex_id].add(begin_vertex_id)

def compute_polygons(polygon_centers: list[Point], polygon_radius: float, number_of_vertices: int) -> list[list[Point]]:
    polygons: list[list[Point]] = []

    for center in polygon_centers:
        polygon: list[Point] = [Point(center.x + polygon_radius, center.y)]

        for vertex_index in range(1, number_of_vertices):
            angle = vertex_index * 2 * math.pi / number_of_vertices
            new_vertex = Point(center.x + polygon_radius * math.cos(angle), center.y + polygon_radius * math.sin(angle))
            polygon.append(new_vertex)

        polygons.append(polygon)

    return polygons

def generate_mesh(polygon_centers: list[Point], polygon_radius: float, number_of_vertices: int) -> Graph:
    graph = Graph()
    polygons: list[list[int]] = []  # A helper list for Stage 4

    # Stage 1: Save a rectangle as polygon data
    save_polygon_elements(graph, polygons, [
        Point(0, 0),
        Point(0, 1),
        Point(1, 1),
        Point(1, 0)
    ])

    # Stage 2: Save polygon data
    for polygon in compute_polygons():
        save_polygon_elements(graph, polygons, polygon)

    # Stage 3: Compute primary segments

# Input parameters

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
