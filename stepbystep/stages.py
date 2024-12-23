"""Defines stages for the current configuration."""

import stepbystep.gen as gen
import ui

# Graph
points: list[gen.Point] = []
connections: dict[int, set[int]] = dict() # The ints are the indices of points from the previous list

polygons: list[list[int]] = [] # A helper list for Stage 4

# Saves the polygon data and draws it on screen
def input_polygon(polygon: list[gen.Point]):
    # Set up graphics - move to the first vertex
    ui.turt.penup()
    ui.turt.setpos(ui.coords(polygon[0].x, polygon[0].y))
    ui.turt.pendown()

    num_vertices = len(polygon)
    first_vertex_id = len(points)

    # Register all the vertices of the polygon
    points.extend(polygon)

    # Save polygon points indices for Stage 4
    polygons.append([first_vertex_id + v for v in range(num_vertices)])

    for begin_vertex_index in range(num_vertices):
        # Get IDs (indices in the points list)
        begin_vertex_id = first_vertex_id + begin_vertex_index
        end_vertex_index = (begin_vertex_index + 1) % num_vertices
        end_vertex_id = first_vertex_id + end_vertex_index

        # Initialize the sets, if the keys are not yet present
        connections.setdefault(begin_vertex_id, set())
        connections.setdefault(end_vertex_id, set())

        # Connect together
        connections[begin_vertex_id].add(end_vertex_id)
        connections[end_vertex_id].add(begin_vertex_id)

        # Draw graphics
        ui.turt.setpos(ui.coords(polygon[end_vertex_index].x, polygon[end_vertex_index].y))

    ui.turt.penup()

# Stage 1
def draw_rectangle():
    ui.turt.clear()
    ui.turt.speed(8)
    ui.turt.width(5)

    input_polygon([
        gen.Point(0, 0),
        gen.Point(0, 1),
        gen.Point(1, 1),
        gen.Point(1, 0)
    ])


# Stage 2
def draw_polygons():
    ui.turt.width(2)

    for polygon in gen.compute_polygons():
        input_polygon(polygon)

# Stage 3
def draw_primary_segments():
    ui.turt.width(1)
    ui.turt.color('blue')

    for rectangle_vertex_idx in range(4):
        for point_idx in range(4, len(points)):
            if gen.segment_intersects_any(points, connections, rectangle_vertex_idx, point_idx):
                continue

            connections[rectangle_vertex_idx].add(point_idx)
            connections[point_idx].add(rectangle_vertex_idx)
            ui.turt.penup()
            ui.turt.setpos(ui.coords(points[rectangle_vertex_idx].x, points[rectangle_vertex_idx].y))
            ui.turt.pendown()
            ui.turt.setpos(ui.coords(points[point_idx].x, points[point_idx].y))

# Stage 4
def draw_secondary_segments():
    ui.turt.width(1)
    ui.turt.color('red')
    ui.turt.speed(20)

    def complete_triangle() -> bool:
        connections_of_polygon_vertices = [
            (0, 1), (1, 0), (1, 2), (2, 1), (2, 3), (3, 2), (0, 3), (3, 0),
            *((poly[v1_idx], poly[v2_idx]) for poly in polygons for v1_idx in range(len(poly)) for v2_idx in range(len(poly)) if v1_idx != v2_idx and (v1_idx + 1) % len(poly) != v2_idx and v1_idx != (v2_idx + 1) % len(poly))
        ]

        # FrEaKy generator expression instead lol
        # for poly in polygons:
        #     for v1_idx in range(len(poly)):
        #         for v2_idx in range(len(poly)):
        #             if v1_idx != v2_idx and (v1_idx + 1) % len(poly) != v2_idx and v1_idx != (v2_idx + 1) % len(poly):
        #                 connections_of_polygon_vertices.append((poly[v1_idx], poly[v2_idx]))

        for a_idx in range(len(points)):
            for b_idx in connections[a_idx]:
                # Look for a 3rd point to complete the triangle
                potential_c_idxs = connections[a_idx].difference(connections[b_idx]).difference({ b_idx })
                for c_idx in potential_c_idxs:
                    if (b_idx, c_idx) in connections_of_polygon_vertices:
                        continue
                    if gen.segment_intersects_any(points, connections, a_idx, c_idx) or gen.segment_intersects_any(points, connections, b_idx, c_idx):
                        continue

                    connections[b_idx].add(c_idx)
                    connections[c_idx].add(b_idx)
                    ui.turt.penup()
                    ui.turt.setpos(ui.coords(points[b_idx].x, points[b_idx].y))
                    ui.turt.pendown()
                    ui.turt.setpos(ui.coords(points[c_idx].x, points[c_idx].y))
                    return False
        return True

    while not complete_triangle():
        pass

STAGES = (
    ("", None),
    ("rectangle", draw_rectangle),
    ("polygons", draw_polygons),
    ("primary segments", draw_primary_segments),
    ("secondary segments", draw_secondary_segments)
)

if __name__ == '__main__':
    print("RUN MESH_GENERATOR.PY, YOU DUMBASS!!! FFS...")
