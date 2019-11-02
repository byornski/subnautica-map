from map import MapObject, Map, triangulate


f = MapObject("P1", 0, 0)
g = MapObject("P2", 0, 4)
h = MapObject("P3", -1, 4)

mainMap = Map()

mainMap.add_reference_point(f)
mainMap.add_reference_point(g)


triangulate(f, g, h, 5.0, 3.0, 2.0)
