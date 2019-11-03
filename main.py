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
root.title("Subnautica Mapper")
w = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="white")

new_mark_name = tk.StringVar(root)


def save_map():
    mainMap.save("map.save")


def load_map():
    global mainMap
    # Load the actual map
    mainMap = Map.load("map.save")

    # Refresh canvas
    w.delete("all")

    # Empty options lists
    opt1.rm_options()
    opt2.rm_options()
    opt3.rm_options()

    # Now add each point to the canvas and options lists
    for marker in mainMap.markers.values():
        draw_point(marker)
        opt1.add_option(marker.name)
        opt2.add_option(marker.name)
        opt3.add_option(marker.name)


def draw_point(marker):
    posX = marker.posX * canvas_scale + canvas_offset_width
    posY = marker.posY * canvas_scale + canvas_offset_height

    point = w.create_oval(posX - marker_size,
                          posY - marker_size,
                          posX + marker_size,
                          posY + marker_size,
                          fill=marker_colour,
                          tag=marker.name)

    text = w.create_text(posX, posY - 3.0 * marker_size, text=marker.name)


def add_point():
    global error_label

    error_label['text'] = ""

    # get distances from gui
    try:
        d1 = opt1.get_dist()
        d2 = opt2.get_dist()
        d3 = opt3.get_dist()

        ref1 = opt1.get_ref()
        ref2 = opt2.get_ref()
        ref3 = opt3.get_ref()
    except ValueError as err:
        error_label['text'] = err
        return

    # Finally get the new name
    point_name = new_mark_name.get()

    if point_name == "" or " " in point_name:
        error_label['text'] = "Must specify a valid name for new point"
        return

    # Now we can actually do the triangulation
    try:
        marker = mainMap.add_point(ref1, ref2, ref3, d1, d2, d3, point_name)
    except AssertionError as err:
        error_label['text'] = err
        return

    # Mark this last point on the actual map
    draw_point(marker)

    # Add to options
    opt1.add_option(marker.name)
    opt2.add_option(marker.name)
    opt3.add_option(marker.name)


class MapReference(object):
    def __init__(self, colour, root, canvas, row, options, name):

        # Save the inputs
        self.name = name
        self.root = root
        self.canvas = canvas
        self.row = row
        self.options = []
        self.colour = colour

        # tk items
        self.label = None
        self.opt_menu = None
        self.dist_entry = None
        self.ref_option = tk.StringVar(root)
        self.mark_dist = tk.StringVar(root)

        # last marked point
        self.canvas_point = None
        self.canvas_circle = None

        # Radius circle
        self.circle_radius = None

        self.draw()

        self.rm_options()
        for i in options:
            self.add_option(i)

    def draw(self):
        self.label = tk.Label(root, text=self.name, bg=self.colour, fg="white", width=50)
        self.label.grid(row=self.row, column=1)

        self.opt_menu = tk.OptionMenu(root, self.ref_option, [], command=self.opt_update())
        self.opt_menu.config(width=20)
        self.opt_menu.grid(row=self.row, column=2, sticky="ew")

        self.dist_entry = tk.Entry(root, textvariable=self.mark_dist)

        self.mark_dist.trace("w", self.text_update())

        self.dist_entry.grid(row=self.row, column=3, pady=10)

    def opt_update(self):
        def callback(value):
            self.redraw_point()
            if self.circle_radius:
                self.redraw_circle()

        return callback

    def text_update(self):
        def callback(*kwargs):
            try:
                self.circle_radius = self.get_dist()
                self.redraw_circle()
                return True
            except ValueError:
                return False

        return callback

    def get_dist(self):
        try:
            return float(self.mark_dist.get())
        except ValueError:
            raise ValueError("Must specify a valid distance!")

    def get_ref(self):
        try:
            return mainMap.markers[self.ref_option.get()]
        except KeyError:
            raise ValueError("Invalid reference point")

    def redraw_point(self):
        # Set old point to black
        if self.canvas_point:
            self.canvas.itemconfig(self.canvas_point, fill="black")

        # Get reference point
        self.canvas_point = self.get_ref().name

        # Mark point
        self.canvas.itemconfig(self.canvas_point, fill=self.colour)

    def rm_options(self):
        m = self.opt_menu.children['menu']
        m.delete(0, 'end')

    def add_option(self, item):
        m = self.opt_menu.children['menu']
        m.add_command(label=item, command=lambda v=self.ref_option, l=item: v.set(l) or self.opt_update()(item))

    def redraw_circle(self):
        # Delete old circle
        if self.canvas_circle:
            self.canvas.delete(self.canvas_circle)

        # Grab point from canvas
        ref = self.get_ref().name
        radius = self.circle_radius

        ax, ay, bx, by = self.canvas.coords(ref)
        px = (ax + bx) // 2
        py = (ay + by) // 2

        self.canvas_circle = \
            self.canvas.create_oval(px - radius * canvas_scale,
                                    py - radius * canvas_scale,
                                    px + radius * canvas_scale,
                                    py + radius * canvas_scale)


w.grid(row=0, columnspan=5)

opt1 = MapReference("blue", root, w, 1, mainMap.markers.keys(), "Reference Point 1")
opt2 = MapReference("red", root, w, 2, mainMap.markers.keys(), "Reference Point 2")
opt3 = MapReference("green", root, w, 3, mainMap.markers.keys(), "Reference Point 3")

tk.Label(root, text="New point name:").grid(row=4, column=1)
tk.Entry(root, textvariable=new_mark_name).grid(row=4, column=2)

tk.Button(root, text="Triangulate", command=add_point, height=5, width=20).grid(row=1, column=4, rowspan=3)
error_label = tk.Label(root, text="", width=20, height=5)
error_label.config(wrap=100)
error_label.grid(row=4, column=4)

tk.Button(root, text="Save", command=save_map, width=40).grid(row=5, column=1, columnspan=2, pady=10)
tk.Button(root, text="Load", command=load_map, width=40).grid(row=5, column=3, columnspan=2)

for marker in mainMap.markers.values():
    draw_point(marker)

tk.mainloop()
