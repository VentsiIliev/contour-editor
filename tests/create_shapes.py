import numpy as np


def create_shapes():
    shapes = {}
    # Rectangle
    rect = np.array([[100,100],[400,100],[400,300],[100,300]])
    shapes["rectangle"] = rect

    # Triangle
    tri = np.array([[250,100],[400,400],[100,400]])
    shapes["triangle"] = tri

    # Circle (approx)
    t = np.linspace(0, 2*np.pi, 100)
    circle = np.column_stack([250 + 150*np.cos(t), 250 + 150*np.sin(t)])
    shapes["circle"] = circle

    # Pentagon
    t = np.linspace(0, 2*np.pi, 6)[:-1]
    pent = np.column_stack([250 + 120*np.cos(t), 250 + 120*np.sin(t)])
    shapes["pentagon"] = pent

    return shapes