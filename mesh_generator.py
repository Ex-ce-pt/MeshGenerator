"""Main file."""

import stepbystep.stages
import ui

STAGES = (
    ("", None),
    ("rectangle", stepbystep.stages.draw_rectangle),
    ("holes", stepbystep.stages.draw_holes),
    ("primary segments", stepbystep.stages.draw_primary_segments),
    ("secondary segments", stepbystep.stages.draw_secondary_segments)
)

def main():
    ui.init_graphics(STAGES)
    ui.window.mainloop()

if __name__ == '__main__':
    main()
