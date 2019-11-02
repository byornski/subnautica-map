from math import sqrt, cos, sin, atan2

small_value = 1.0e-6
dist_tol = 1.0e-1

class MapObject(object):
    """A single entity on the map"""

    def __init__(self, name: str, posx: float, posy: float):
        """Initialise a map entry from a position"""
        self.name = name
        self.posX = posx
        self.posY = posy

    def distance(self, other: 'MapObject') -> float:
        """Returns the distance to another object"""
        return self.distance_to_pos(other.pos())

    def distance_to_pos(self, pos):
        diff_x = self.posX - pos[0]
        diff_y = self.posY - pos[1]
        return sqrt(diff_x ** 2 + diff_y ** 2)


    def __repr__(self):
        """Get a string representation of the object"""
        return "{} : ({},{})".format(self.name, self.posX, self.posY)

    def pos(self):
        return self.posX, self.posY


def rotate(pos, angle: float):
    return (
        pos[0] * cos(angle) - pos[1] * sin(angle),
        pos[0] * sin(angle) + pos[1] * cos(angle)
    )


def translate(pos, origin, factor=1.0):
    return (
        pos[0] - factor * origin[0],
        pos[1] - factor * origin[1]
    )


class Map(object):
    """The entire map"""

    def __init__(self):
        """Initialises the map as empty"""
        self.num_markers = 0
        self.markers = []

    def add_reference_point(self, reference_point: MapObject):
        """Adds a reference point to the map"""
        self.markers.append(reference_point)

    def add_point(self, ref1: MapObject, ref2: MapObject, ref3: MapObject, r1: float, r2: float, r3: float, name: str):
        """Add a point by triangulation to reference points"""


def triangulate(ref1: MapObject, ref2: MapObject, ref3: MapObject, r1: float, r2: float, r3: float):
    # Get circle positions
    p1 = ref1.pos()
    p2 = ref2.pos()
    p3 = ref3.pos()

    # Translate so that p1 is the origin
    origin_pos = p1
    p1 = translate(p1, origin_pos)
    p2 = translate(p2, origin_pos)
    p3 = translate(p3, origin_pos)

    assert abs(p1[0]) < small_value, "Translation in x didn't work!"
    assert abs(p1[1]) < small_value, "Translation in y didn't work!"

    # Find rotation angle so that p2 is along +x
    rot_angle = -atan2(p2[1], p2[0])
    p1 = rotate(p1, rot_angle)
    p2 = rotate(p2, rot_angle)
    p3 = rotate(p3, rot_angle)

    assert abs(p2[1]) < small_value, "Rotation didn't work! -- y not 0"
    assert p2[0] > 0.0, "Rotation didn't work! -- x value negative"

    # Calculate x'' from equations 1 and 2
    # https://en.wikipedia.org/wiki/True_range_multilateration#Three_Cartesian_dimensions,_three_measured_slant_ranges
    d3 = p3[0] ** 2 + p3[1] ** 2
    xrot = (p2[0] ** 2 + r1 ** 2 - r2 ** 2) / (2. * p2[0])
    yrot = (r1 ** 2 - r3 ** 2 + d3 - 2.0 * p3[0] * xrot) / (2.0 * p3[1])
    pos = (xrot, yrot)

    # Now rotate back to original coordinate rotation and translate to correct origin
    pos = rotate(pos, -rot_angle)
    pos = translate(pos, origin_pos, factor=-1.0)

    # Check distances to reference points
    assert abs(ref1.distance_to_pos(pos) - r1) < dist_tol, "Final position is not the correct distance from ref 1"
    assert abs(ref2.distance_to_pos(pos) - r2) < dist_tol, "Final position is not the correct distance from ref 2"
    assert abs(ref3.distance_to_pos(pos) - r3) < dist_tol, "Final position is not the correct distance from ref 3"

    return pos
