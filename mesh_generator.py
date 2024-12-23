"""Main file."""

import stepbystep
from stepbystep import stages
import full
from full import stages
import ui

# 0 - Step-by-step
# 1 - Full computation
config = 0

def main():
    match config:
        case 0:
            ui.init_graphics(stepbystep.stages.STAGES)

        case 1:
            ui.init_graphics(full.stages.STAGES)

        case _:
            print("Unsupported configuration:", config)
            exit(1)

    ui.window.mainloop()

if __name__ == '__main__':
    main()
