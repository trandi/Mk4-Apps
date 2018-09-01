"""Game of Life"""

___name___         = "Conway game of life"
___license___      = "MIT"
___categories___   = ["Games"]
___dependencies___ = ["app", "ugfx_helper", "random", "sleep", "buttons"]

import ugfx, ugfx_helper, buttons, sleep, time, random
from tilda import Buttons


# the game of life logic
class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.data = [random.randint(0, 1) for x in range(width * height)]

    def __str__(self):
        res  = "w: {}  h: {}".format(self.width, self.height)
        for j in range(0, self.height):
            row = [self.value(i, j) for i in range(0, self.width)]
            res = res + "\n" + row
        return res

    def value(self, x, y):
        return self.data[x * self.width + y]

    def neighbours(self, x, y):
        neighbCoords = [(i, j) 
            for i in range(x - 1, x + 2) if i >= 0 and i < self.width
            for j in range(y - 1, y + 2) if j >= 0 and j < self.height
        ]

        return [self.value(neighbCoord[0], neighbCoord[1]) 
                for neighbCoord in neighbCoords if neighbCoord != (x, y) ]

    # returns the new value of a given cell
    def updateCell(self, x, y):
        neighbsArr = self.neighbours(x, y)
        liveNeighbs = 0
        for neighb in neighbsArr:
            if (neighb):
                liveNeighbs = liveNeighbs + 1

        if(self.value(x, y)):
            if (liveNeighbs <= 1):
                return 0    # underpopulation
            else:
                if (liveNeighbs <= 3):
                    return 1    # lives
                else:
                    return 0    # overpopulation
        else:
            if (liveNeighbs == 3):
                return 1    # reproduction
            else:
                return 0    # dies
        
    # update the board data in place by creating a new board with the updated cells and then swaping it
    def step(self):
        allCoords = [(x, y) for x in range(0, self.width) for y in range(0, self.height)]
        updatedData = [self.updateCell(c[0], c[1]) for c in allCoords]
        self.data = updatedData



# now the displaying part

ugfx_helper.init()
ugfx.clear()


grid_size = 5
grid_width = ugfx.width() / grid_size
grid_height = ugfx.height() / grid_size
alive_colour = ugfx.WHITE
dead_colour = ugfx.BLACK

def displayCell(x, y, alive):
    if(alive):
        colour = alive_colour
    else:
        colour = dead_colour
    ugfx.area((x+1)*grid_size, (y+1)*grid_size, grid_size, grid_size, colour)


def displayBoard(board):
    coords = [(x, y) for x in range(0, board.x) for y in range(0, board.y)]
    for (x, y) in coords:
        displayCell(x, y, board.value(x, y))
    



board = Board(grid_width, grid_height)
while True:
    board.step()
    displayBoard(board)
    time.sleep(1)

    sleep.wfi()
    if buttons.is_triggered(Buttons.BTN_Menu):
        break


ugfx.clear()
app.restart_to_default()
