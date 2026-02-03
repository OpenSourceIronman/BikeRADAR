#!/usr/bin/env python
# https://github.com/gboeing/osmnx-examples/tree/main/notebooks
# https://wiki.openstreetmap.org/wiki/OSMnx

import osmnx as ox
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

#import SlippyMap

def build_road_network(mapCenter: tuple, radius: int = 3200, colsolidated: bool = False):
    """
    Builds a road network using OpenStreetMap data.

    Args:
        mapCenter (tuple): The center point of the map in (latitude, longitude) format
        radius (int): The sqare radius of the map in meters

    Returns:
        osmnx.graph.Graph: The road network graph.
    """
    graph = ox.graph_from_point(mapCenter, dist=radius, network_type="bike")

    if colsolidated:
        G_proj = ox.projection.project_graph(graph)
        colsolidatedGraph = ox.simplification.consolidate_intersections(
            G_proj,
            rebuild_graph=True,
            tolerance=10,
            dead_ends=False)
        return colsolidatedGraph
    else:
        return graph

    #osmnx.bearing.add_edge_bearings(osmxGraph)

def visualize_road_network(osmxGraph):
    fig, ax = ox.plot_graph(osmxGraph)

def animate_dot(osmxGraph, path_latlng):
    # 1. Plot the graph (get fig, ax)
    fig, ax = ox.plot_graph(osmxGraph, show=False, close=False)

    # 2. Extract lat/lon arrays for animation
    lat = np.array([p[0] for p in path_latlng])
    lon = np.array([p[1] for p in path_latlng])

    # 3. Convert lat/lon to same coordinate system as OSMnx plot
    #    (OSMnx plots projected graphs unless specified)
    try:
        gproj = ox.projection.project_graph(osmxGraph)
        x, y = ox.projection.project_geometry(lon, lat)
    except:
        # If graph is not projected, fallback to lon/lat directly
        x, y = lon, lat

    # 4. Create the red dot
    dot, = ax.plot([], [], 'ro', markersize=8)

    # 5. Animation update function
    def update(frame):
        dot.set_data([x[frame]], [y[frame]])
        return dot,

    # 6. Run animation
    ani = FuncAnimation(fig, update, frames=len(x), interval=150, blit=True)

    plt.show()

def main():
    mapCenter = (36.144635, -115.326555)
    G = build_road_network(mapCenter)

    # Small test path
    path = [
        (36.144486, -115.326555),
        (36.144486, -115.326400),
        (36.144486, -115.326250),
        (36.144486, -115.326100),
        (36.144486, -115.325950),
    ]

    animate_dot(G, path)

def turn_left(degree: int) -> bool:

    return True

def turn_right(degree: int) -> bool:

    return True

def unit_test():
    assert True
    fakeData = Faker()
    Faker.seed(42)

    print(f"{fakeData.city()} with {Faker.seed}")

if __name__ == "__main__":

    #unit_test()
    main()


"""
import osmnx as ox
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

def animate_dot(osmxGraph, path_latlng):
    # 1. Plot the graph (get fig, ax)
    fig, ax = ox.plot_graph(osmxGraph, show=False, close=False)

    # 2. Extract lat/lon arrays for animation
    lat = np.array([p[0] for p in path_latlng])
    lon = np.array([p[1] for p in path_latlng])

    # 3. Convert lat/lon to same coordinate system as OSMnx plot
    #    (OSMnx plots projected graphs unless specified)
    try:
        gproj = ox.projection.project_graph(osmxGraph)
        x, y = ox.projection.project_geometry(lon, lat)
    except:
        # If graph is not projected, fallback to lon/lat directly
        x, y = lon, lat

    # 4. Create the red dot
    dot, = ax.plot([], [], 'ro', markersize=8)

    # 5. Animation update function
    def update(frame):
        dot.set_data(x[frame], y[frame])
        return dot,

    # 6. Run animation
    ani = FuncAnimation(fig, update, frames=len(x), interval=150, blit=True)

    plt.show()

def main():
    mapCenter = (36.144635, -115.326555)

    # Build the graph
    G = build_road_network(mapCenter)

    # Example path of red-dot movement (lat, lon pairs)
    # You would replace this with your own GPS path or route
    path = [
        (36.144635, -115.326555),
        (36.144700, -115.326400),
        (36.144800, -115.326250),
        (36.144900, -115.326100),
        (36.145000, -115.325950),
    ]

    animate_dot(G, path)

if __name__ == "__main__":
    main()

"""
