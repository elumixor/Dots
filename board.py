from typing import Dict

from p5 import *

from common import min_value, max_value, distance
from grid import Grid
from parameters import *


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.position = (x, y)
        self.connections = []

    def __repr__(self):
        return str(self.position)

    def connect(self, other: 'Point'):
        if other not in self.connections:
            self.connections.append(other)
            other.connections.append(self)
        else:
            raise Exception(f"{self} and {other} are already connected.")

    @property
    def magnitude(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def distance(self, other):
        return distance(self.position, other.position)

    def __float__(self):
        return self.magnitude

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __getitem__(self, item):
        return self.position[item]

    @staticmethod
    def random(player=round(random_uniform(number_of_players - 1))):
        x = round(random_uniform(board_size - 1))
        y = round(random_uniform(board_size - 1))
        return x, y, player


class Cycle:
    def __init__(self, points):
        self.points = points
        self.captured_points = []

        # find bounds of a cycle
        max_x = max_y = min_value
        min_x = min_y = max_value

        for p in points:
            if p.x > max_x:
                max_x = p.x
            if p.x < min_x:
                min_x = p.x
            if p.y > max_y:
                max_y = p.y
            if p.y < min_y:
                min_y = p.y

        for y in range(min_y + 1, max_y):
            for x in range(min_x + 1, max_x):
                has_bound = False
                for y1 in range(y - 1, min_y - 1, -1):
                    if Point(x, y1) in points:
                        has_bound = True
                        break
                if not has_bound:
                    continue

                has_bound = False
                for y1 in range(y + 1, max_y + 1):
                    if Point(x, y1) in points:
                        has_bound = True
                        break
                if not has_bound:
                    continue

                has_bound = False
                for x1 in range(x - 1, min_x - 1, -1):
                    if Point(x1, y) in points:
                        has_bound = True
                        break
                if not has_bound:
                    continue

                has_bound = False
                for x1 in range(x + 1, max_x + 1):
                    if Point(x1, y) in points:
                        has_bound = True
                        break
                if not has_bound:
                    continue

                # add to captured points
                self.captured_points.append(Point(x, y))

    def __eq__(self, other):
        length = len(self.points)

        if length != len(other.points):
            return False

        same = True

        # normal order
        for i in range(0, length):
            if self.points[i] != other.points[i]:
                # normal order not ok
                same = False
                break

        # normal order ok
        if same:
            return True

        # reverse order
        for i in range(0, length):
            if self.points[i] != other.points[length - i - 1]:
                # reverse order not ok
                return False

        # reverse order ok
        return True

    def __getitem__(self, item):
        return self.points[item]

    def __len__(self):
        return len(self.points)

    def __str__(self):
        return str(self.points)


class Group:
    def __init__(self, player: int = -1):
        self.player = player
        self.points: [Point] = []

    def add_point(self, x, y):
        """
        Adds a point to a group. Inserts new point after the closest one, and connects those points
        :param x: x coordinate
        :param y: y coordinate
        :returns True if a close point was found, and new point was successfully added
        """

        p = Point(x, y)

        if not self.points:
            self.points.append(p)
        else:
            connected_points = []

            d = max_value
            i = 0

            for (i1, p1) in enumerate(self.points):
                d1 = p1.distance(p)
                if d1 < d:
                    i = i1
                    d = d1

                if d1 >= 2:
                    continue

                if [p2 for p2 in p1.connections if p.distance(p2) < 2 and p2 not in connected_points]:
                    connected_points.append(p1)
                    continue

                connected_points.append(p1)
                p.connect(p1)

            if d >= 2:
                return False

            self.points.insert(i, p)

        return True

    def merge_with_group(self, other: 'Group'):
        """
        Merges this groups with the other. Supposes that two groups have one touching point
        :param other: Group to be merged with
        """

        # suppose we have one touching point, then for single point distance will be < 2
        for p1 in self.points:
            for p2 in other.points:
                if p1.distance(p2) < 2:
                    self.points.extend(other.points)
                    p1.connect(p2)
                    return True

        return False

    def capture_points(self, captured_points):
        # should return group of captured points and array of remaining groups

        # for captured, we can simply append all points, as we don't care about connecting new ones
        captured = Group()
        captured.points = [Point(*p) for p in captured_points]

        remaining_points = [p for p in self.points if p.position not in captured_points]

        if len(remaining_points) == 0:
            return captured, []

        # initialize remaining groups with single group containing first remaining point
        remaining_groups = [Group(self.player)]
        remaining_groups[0].add_point(*remaining_points[0].position)

        # create new groups from remaining points
        for p in remaining_points[1:]:
            group_found = False
            for g in remaining_groups:
                if g.add_point(*p):
                    group_found = True
                    break

            if not group_found:
                g = Group(self.player)
                g.add_point(*p)
                remaining_groups.append(g)

        return captured, remaining_groups

    @property
    def cycles(self):
        result_cycles = []

        # recursively go through points
        # when point is found in the path, then we have probably formed a cycle if:
        #   1. cycle contains 4+ points (starting from the first occurrence of current point)
        #   2. we never went backwards
        def _get_cycles(current, path):
            next_path = path.copy()
            next_path.append(current)

            # cycle suspicious
            path_length = len(path)
            if path_length > 0 and current in path:
                cycle = Cycle(next_path[path.index(current):])
                if cycle not in result_cycles and len(cycle.captured_points) > 0:
                    result_cycles.append(cycle)
                return

            # check that we neither go backwards, nor through smaller cycles
            next_points = [p for p in current.connections if p not in path or path_length - path.index(p) >= 3]
            for p in next_points:
                _get_cycles(p, next_path)

        _get_cycles(self.points[0], [])
        return result_cycles

    def __str__(self):
        return f"Group: {str(self.points)}"

    def __repr__(self):
        return str(self)


class Board:
    def __init__(self, grid: Grid):
        self.grid = grid

        # array of points, every point contains group reference
        self.points: [[Group]] = [[None for x in range(0, board_size)] for y in range(0, board_size)]
        self.groups = [[] for i in players]
        self.cycles = [[] for i in players]

        # captured points are unavailable for future point placement
        self.captured_points = []

    def place_dot(self, x: int, y: int, player):
        """
        Places new dot on the board
        :returns True if dot was placed, else False
        """
        if self.points[y][x] is not None:
            print(f"Point at {(x, y)} already exists.")
            return False

        if Point(x, y) in self.captured_points:
            print(f"Point at {(x, y)} cannot be placed because it is in the captured points.")
            return False

        # we need to update groups and check if we had created any cycles

        # we start by checking if new point has any groups around it
        # we create a dict of group -> surrounding points of that group
        surrounding_groups = self.get_surrounding_groups(x, y, player)

        print(f"Surrounding groups for {(x, y)}: [{', '.join([str(g) for g in surrounding_groups])}]")

        # if any surrounding points were found, merge groups together with
        # a new point, update cycles and captured points
        if len(surrounding_groups) > 0:
            # create resulting group
            resulting_group = list(surrounding_groups)[0]

            resulting_group.add_point(x, y)

            for g in surrounding_groups[1:]:
                resulting_group.merge_with_group(g)
                self.groups[player].remove(g)

            # set points in the group on the board to reference resulting group
            for p in resulting_group.points:
                self.points[p.y][p.x] = resulting_group

            # get cycles from this group
            cycles = resulting_group.cycles

            # update board's cycles
            for cycle in cycles:
                if cycle not in self.cycles[player]:
                    self.cycles[player].append(cycle)

                    # create an array of pairs: ([points], groups)
                    group_points = dict()

                    captured_points = cycle.captured_points

                    # update board's captured points
                    for p in captured_points:
                        # if not captured yet, add this group
                        if p not in self.captured_points:
                            self.captured_points.append(p)

                            p1 = self.points[p.y][p.x]
                            if p1 is not None:
                                if p1 in group_points:
                                    group_points[p1].append((p.x, p.y))
                                else:
                                    group_points[p1] = [(p.x, p.y)]

                        # if it is captured, switch it's group
                        else:
                            self.points[p.y][p.x].player = player

                        # for each cycle that is inside the captured cycle it should be reversed:
                        # for each captured point, if it belongs to a cycle of a different player,
                        # that cycle should be switched, if captured, switch the cycle
                        if self.points[p.y][p.x] is not None and self.points[p.y][p.x].player != player:
                            previous = self.points[p.y][p.x].player

                            # for each cycle that contains this point
                            # remove that cycle from that cycle's player's cycles array
                            # and append it to a new player's cycles
                            to_remove = []

                            for c1 in self.cycles[previous]:
                                if p in c1 and c1 not in to_remove:
                                    to_remove.append(c1)

                            for c1 in to_remove:
                                self.cycles[previous].remove(c1)
                                self.cycles[player].append(c1)

                    for g in group_points:
                        # for this captured point, it should be separated from the group
                        captured, slices = g.capture_points(group_points[g])

                        # captured should be added as a new group, of a capturing (active) player
                        captured.player = player
                        self.groups[player].append(captured)

                        for p in captured.points:
                            self.points[p.y][p.x] = captured

                        # slices should be added as a new group
                        for s in slices:
                            for p2 in s.points:
                                self.points[p2.y][p2.x] = s

                            self.groups[s.player].append(s)

                        # previous group should be removed
                        self.groups[g.player].remove(g)

        # if no surrounding points were found, create simply add this point to a new group
        else:
            group = Group(player)
            group.add_point(x, y)
            self.points[y][x] = group
            self.groups[player].append(group)
        return True

    def get_surrounding_groups(self, x, y, player) -> set:
        groups = set()

        has_left = x > 0
        has_right = x < board_size - 1
        has_top = y > 0
        has_bottom = y < board_size - 1

        def add_point(px, py):
            g = self.points[py][px]
            if g is not None and g.player == player:
                groups.add(g)

        if has_top:
            add_point(x, y - 1)
            if has_left:
                add_point(x - 1, y - 1)
            if has_right:
                add_point(x + 1, y - 1)

        if has_bottom:
            add_point(x, y + 1)
            if has_left:
                add_point(x - 1, y + 1)
            if has_right:
                add_point(x + 1, y + 1)

        if has_left:
            add_point(x - 1, y)
        if has_right:
            add_point(x + 1, y)

        return list(groups)

    def render(self):
        self.grid.render()
        self.render_points()
        self.render_lines()

    def render_points(self):
        for (y, row) in enumerate(self.points):
            for (x, group) in enumerate(row):
                if group is not None:
                    self.render_point(x, y, group.player)

    def render_lines(self):
        for [player, cycles] in enumerate(self.cycles):
            for cycle in cycles:
                length = len(cycle)
                for i in range(0, length - 1):
                    self.render_line(cycle[i], cycle[i + 1], player)

    def render_point(self, x, y, player):
        position = self.grid.map_line_point((x, y))
        fill(colors[player])
        circle(position, dot_radius, 'RADIUS')

    def render_line(self, start: [], end: [], player: int):
        stroke(colors[player])
        line(self.grid.map_line_point(start), self.grid.map_line_point(end))

    def print(self):
        for player in players:
            print(f"Player: {colors[player]}")

            print(f"\tGroups: ({len(self.groups[player])})")
            for (i, group) in enumerate(self.groups[player]):
                print(f"\t\t{i}: {str(group)}")
            print()

            print(f"\tCycles: ({len(self.cycles[player])})")
            for (i, cycle) in enumerate(self.cycles[player]):
                print(f"\t\t{i}: {str(cycle)}")
            print()

    def score(self, player):
        s = 0

        for y in range(0, board_size):
            for x in range(0, board_size):
                g = self.points[y][x]
                if g is not None and g.player == player:
                    s += 1

        return s
