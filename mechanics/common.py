from math import sqrt


class _max:
    def __lt__(self, other): return False

    def __gt__(self, other): return True


class _min:
    def __lt__(self, other): return True

    def __gt__(self, other): return False


max_value, min_value = _max(), _min()


def distance(p1, p2):
    x = p2[0] - p1[0]
    y = p2[1] - p1[1]
    return sqrt(x * x + y * y)


mdown = False


def get_mouse_down():
    global mouse_is_pressed
    global mdown

    if mouse_is_pressed:
        if not mdown:
            mdown = True
            return True
        return False
    else:  # not pressed
        mdown = False
        return False
