from p5 import line, stroke


class Grid:
    lines: int
    line_thickness: float
    space_thickness: float
    scale: float = 1
    window_size: float

    vertical_lines: [((float, float), (float, float))]
    horizontal_lines: [((float, float), (float, float))]

    def __init__(self, lines: int, line_thickness: float, space_thickness: float, scale: float = 1):
        self.lines = lines
        self.line_thickness = line_thickness
        self.space_thickness = space_thickness
        self.scale = scale
        self.window_size = (lines * (line_thickness + space_thickness) + space_thickness) * scale

        def p(i: float):
            return self.map((i + 1) / (lines + 1))

        self.vertical_lines = [(
            (p(i), 0), (p(i), self.window_size)
        ) for i in range(0, lines)]

        self.horizontal_lines = [(
            (0, p(i)), (self.window_size, p(i))
        ) for i in range(0, lines)]

    @property
    def size(self):
        return self.window_size, self.window_size

    def render(self):
        stroke("black")

        for i in range(0, self.lines):
            line(*(self.vertical_lines[i]))
            line(*(self.horizontal_lines[i]))

    def map(self, x: float):
        """
        Maps a value from (0, 1) range to window space
        """
        return self.window_size * x

    def map_line_point(self, dot):
        return tuple(self.map((d + 1) / (self.lines + 1)) for d in dot)

    def map_from_mouse(self, mouse_x, mouse_y):
        x = min(self.lines - 1, max(0, round(mouse_x / self.window_size * (self.lines + 1)) - 1))
        y = min(self.lines - 1, max(0, round(mouse_y / self.window_size * (self.lines + 1)) - 1))
        return int(x), int(y)
    
