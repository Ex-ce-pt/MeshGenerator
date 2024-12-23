"""Defines stages for the current configuration."""

import full.gen as gen
import ui
import time

####################################
# Input
POLYGON_RADIUS: float = 0.1
POLYGON_CENTERS: list[gen.Point] = [
    gen.Point(0.5, 0.5),
    gen.Point(0.3, 0.25),
    gen.Point(0.8, 0.8),
    gen.Point(0.2, 0.85)
]
NUMBER_OF_VERTICES: int = 10
####################################

graph = None

def time_compute_mesh():
    global graph

    start_time = time.time_ns()

    graph = gen.generate_mesh(POLYGON_CENTERS, POLYGON_RADIUS, NUMBER_OF_VERTICES)

    print("Calculated the mesh, elapsed", (time.time_ns() - start_time), " ns")

def draw_mesh():
    pass

STAGES = (
    ("", None),
    ("Computed mesh", draw_mesh)
)

if __name__ == '__main__':
    print("RUN MESH_GENERATOR.PY, YOU DUMBASS!!! FFS...")
