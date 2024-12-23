"""File responsible for handling the UI."""

import turtle
import tkinter as tk

CANVAS_WIDTH = 600
CANVAS_HEIGHT = 600

window: tk.Tk | None = None
turt: turtle.RawTurtle | None = None
label: tk.Label | None = None
stage: int = 0
stage_in_progress: bool = False
stage_text_variable: tk.StringVar | None = None
stages = []

def coords(x: float, y: float) -> tuple[float, float]:
    return (x - 0.5) * CANVAS_WIDTH, (y - 0.5) * CANVAS_HEIGHT

def get_label_name():
    return f'Stage {stage}: {stages[stage][0]}'

def advance_stage():
    global stage
    global stage_in_progress

    if stage_in_progress:
        return
    stage += 1
    if stage >= len(stages):
        return
    stage_text_variable.set(get_label_name())
    if stages[stage][1] is not None:
        stage_in_progress = True
        stages[stage][1]()
        stage_in_progress = False

def init_graphics(stages_list: list[tuple[str, any]]):
    global window
    global turt
    global label
    global stage_text_variable
    global stages

    stages = stages_list

    window = tk.Tk("Mesh Generator")

    canvas = tk.Canvas(window)
    canvas.config(width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
    canvas.pack(side=tk.LEFT)

    screen = turtle.TurtleScreen(canvas)
    screen.bgcolor("white")

    stage_text_variable = tk.StringVar()
    stage_text_variable.set(get_label_name())

    label = tk.Label(textvariable=stage_text_variable)
    label.pack(side=tk.RIGHT)

    button = tk.Button(text='Next', command=advance_stage)
    button.pack(side=tk.RIGHT)

    turt = turtle.RawTurtle(screen, shape="triangle")
    turt.penup()
    turt.speed(2)

if __name__ == '__main__':
    print("RUN MESH_GENERATOR.PY, YOU DUMBASS!!! FFS...")
