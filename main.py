from map import MapObject, Map, triangulate
import tkinter as tk

f = MapObject("Base", 0, 0)
g = MapObject("Beacon1", 0, 400)
h = MapObject("Beacon2", -100, 400)

mainMap = Map()

mainMap.add_reference_point(f)
mainMap.add_reference_point(g)
mainMap.add_reference_point(h)

# Set canvas width and height
canvas_width = 1000
canvas_height = 800

# Origin in them middle
canvas_offset_width = 500
canvas_offset_height = 400

# Canvas zoom
canvas_scale = 0.5

# Size of points
marker_size = 5.0
marker_colour = "black"

root = tk.Tk()
w = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="white")

# Marked points

ref1_option = tk.StringVar(root)
ref2_option = tk.StringVar(root)
ref3_option = tk.StringVar(root)

mark1_point = None
mark2_point = None
mark3_point = None

mark1_circle = None
mark2_circle = None
mark3_circle = None

d1_circle_tag = "d1_circle_tag"
d2_circle_tag = "d2_circle_tag"
d3_circle_tag = "d3_circle_tag"

mark1_colour = "blue"
mark2_colour = "red"
mark3_colour = "green"

mark1_dist = tk.StringVar(root)
mark2_dist = tk.StringVar(root)
mark3_dist = tk.StringVar(root)

opt1_menu = None
opt2_menu = None
opt3_menu = None

newmark_name = tk.StringVar(root)


def save_map():
    mainMap.save("map.save")


def load_map():
    global mainMap
    # Load the actual map
    mainMap = Map.load("map.save")

    # Refresh canvas

    w.delete("all")
    for marker in mainMap.markers.values():
        draw_point(marker)


def draw_circle(coords, radius, tag):
    ax, ay, bx, by = coords
    px = (ax + bx) // 2
    py = (ay + by) // 2
    w.create_oval(px - radius, py - radius, px + radius, py + radius, tag=tag)


def mark1(opt=None):
    global mark1_point

    if opt:
        ref1_option.set(opt)

    w.delete(d1_circle_tag)
    w.itemconfig(mark1_point, fill=marker_colour)
    mark1_point = ref1_option.get()
    w.itemconfig(mark1_point, fill=mark1_colour)

    # Draw a circle if the radius has been given
    try:
        d1 = float(mark1_dist.get()) * canvas_scale
    except ValueError:
        return False

    draw_circle(w.coords(mark1_point), d1, d1_circle_tag)
    return True


def mark2(opt=None):
    global mark2_point

    if opt:
        ref2_option.set(opt)

    w.delete(d2_circle_tag)
    w.itemconfig(mark2_point, fill=marker_colour)
    mark2_point = ref2_option.get()
    w.itemconfig(mark2_point, fill=mark2_colour)

    # Draw a circle if the radius has been given
    try:
        d2 = float(mark2_dist.get()) * canvas_scale
    except ValueError:
        return False

    draw_circle(w.coords(mark2_point), d2, d2_circle_tag)
    return True


def mark3(opt=None):
    global mark3_point

    if opt:
        ref3_option.set(opt)

    w.delete(d3_circle_tag)
    w.itemconfig(mark3_point, fill=marker_colour)
    mark3_point = ref3_option.get()
    w.itemconfig(mark3_point, fill=mark3_colour)

    # Draw a circle if the radius has been given
    try:
        d3 = float(mark3_dist.get()) * canvas_scale
    except ValueError:
        return False

    draw_circle(w.coords(mark3_point), d3, d3_circle_tag)
    return True


def draw_point(marker, circle_radius=None, circle_marker=None):
    global opt1_menu, opt2_menu, opt3_menu

    posX = marker.posX * canvas_scale + canvas_offset_width
    posY = marker.posY * canvas_scale + canvas_offset_height

    point = w.create_oval(posX - marker_size,
                          posY - marker_size,
                          posX + marker_size,
                          posY + marker_size,
                          fill=marker_colour,
                          tag=marker.name)

    text = w.create_text(posX, posY - 3.0 * marker_size, text=marker.name)

    # Add to options lists
    add_to_list(opt1_menu, marker.name, ref1_option, mark1)
    add_to_list(opt2_menu, marker.name, ref2_option, mark2)
    add_to_list(opt3_menu, marker.name, ref3_option, mark3)


def add_to_list(menu, item, ref_opt, mark_cmd):
    m = menu.children['menu']
    m.add_command(label=item, command=lambda v=ref_opt, l=item: v.set(l) or mark_cmd())


def add_point():
    # get distances from gui
    try:
        d1 = float(mark1_dist.get())
    except ValueError:
        raise Exception("Must specify a distance to point 1")

    try:
        d2 = float(mark2_dist.get())
    except ValueError:
        raise Exception("Must specify a distance to point 2")

    try:
        d3 = float(mark3_dist.get())
    except ValueError:
        raise Exception("Must specify a distance to point 3")

    # get reference points
    try:
        ref1 = mainMap.markers[ref1_option.get()]
    except KeyError:
        raise Exception("Invalid reference for point 1")

    try:
        ref2 = mainMap.markers[ref2_option.get()]
    except KeyError:
        raise Exception("Invalid reference for point 2")

    try:
        ref3 = mainMap.markers[ref3_option.get()]
    except KeyError:
        raise Exception("Invalid reference for point 3")

    # Finally get the new name
    point_name = newmark_name.get()

    # Now we can actually do the triangulation
    marker = mainMap.add_point(ref1, ref2, ref3, d1, d2, d3, point_name)

    # Mark this last point on the actual map
    draw_point(marker)



class mapReference(object):
    def __init__(self, colour, root, row, options, name):

        # Save the inputs
        self.name = name
        self.root = root
        self.row = row
        self.options = options
        self.colour = colour

        # tk items
        self.label = None
        self.opt_menu = None
        self.dist_entry = None
        self.option_selected = tk.StringVar(root)
        self.mark_dist = tk.StringVar(root)

        # last marked point
        self.mark_point = None
        self.mark_circle = None
        self.circle_tag = name.replace(" ", "") + "-circle-" + str(row)
        print(self.circle_tag)


    def draw(self):
        self.label = tk.Label(root, text=self.name, bg=self.colour, fg="white")
        self.label.grid(row=self.row, column=1)
        self.opt_menu = tk.OptionMenu(root, ref1_option, [], command=mark1)
        self.opt_menu.grid(row=self.row, column=2)
        self.dist_entry = tk.Entry(root, textvariable=mark1_dist, validate="focusout", validatecommand=mark1)
        self.dist_entry.grid(row=self.row, column=3)

    def opt_update(self):
        pass






def draw_window(root, w):
    global opt1_menu, opt2_menu, opt3_menu



    w.grid(row=0, columnspan=5)

    tk.Label(root, text="Reference Point 1", bg=mark1_colour, fg="white").grid(row=1, column=1)
    opt1_menu = tk.OptionMenu(root, ref1_option, [], command=mark1)
    opt1_menu.grid(row=1, column=2)
    tk.Entry(root, textvariable=mark1_dist, validate="focusout", validatecommand=mark1).grid(row=1, column=3)

    tk.Label(root, text="Reference Point 2", bg=mark2_colour, fg="white").grid(row=2, column=1)
    opt2_menu = tk.OptionMenu(root, ref2_option, [], command=mark2)
    opt2_menu.grid(row=2, column=2)
    tk.Entry(root, textvariable=mark2_dist, validate="focusout", validatecommand=mark2).grid(row=2, column=3)

    tk.Label(root, text="Reference Point 3", bg=mark3_colour, fg="white").grid(row=3, column=1)
    opt3_menu = tk.OptionMenu(root, ref3_option, [], command=mark3)
    opt3_menu.grid(row=3, column=2)
    tk.Entry(root, textvariable=mark3_dist, validate="focusout", validatecommand=mark3).grid(row=3, column=3)

    tk.Label(root, text="New point name:").grid(row=4, column=1)
    tk.Entry(root, textvariable=newmark_name).grid(row=4, column=3)

    tk.Button(root, text="Triangulate", command=add_point).grid(row=1, column=4, rowspan=4)

    tk.Button(root, text="Save", command=save_map, width=50).grid(row=5, column=1, columnspan=2)
    tk.Button(root, text="Load", command=load_map, width=50).grid(row=5, column=3, columnspan=2)

    for marker in mainMap.markers.values():
        draw_point(marker)


    tk.mainloop()


draw_window(root, w)
