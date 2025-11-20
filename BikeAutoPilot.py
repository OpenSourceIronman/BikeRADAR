#!

import networkx as nx
import osmnx as ox      # pip install osmnx



from SlippyMap import *

osmxGraph = None

def build_road_network(m: SlippyMap):

    point = m.mapCenter
    radius = 1000 # Meters
    osmxGraph = ox.graph_from_point(point, dist=radius, network_type="bike")
    
    osmnx.bearing.add_edge_bearings(osmxGraph)


def visualize_road_network():
    fig, ax = ox.plot_graph(osmxGraph)


def turn_left(degree: int) -> bool:

    return True

def turn_right(degree: int) -> bool:

    return True


def main():


def unit_test():
    assert True   

if __name__ == "__main__":
    main()