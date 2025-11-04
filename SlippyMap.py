#!/usr/bin/env python

# Translates between lat/long and the slippy-map tile numbering scheme
# http://wiki.openstreetmap.org/index.php/Slippy_map_tilenames
# https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
# https://en.wikipedia.org/wiki/Tiled_web_map
# https://quad.osm.lol/
#
# Written by Oliver White, 2007
# https://github.com/openstreetmap/svn-archive/blob/main/applications/routing/pyroute/tilenames.py
#
# Updated by Blaze Sanders, 2025
# TODO: GITHUB LINK

import math

from nicegui import ui

TILE_SIZE = 256
GPS_DECIMAL_ROUNDING = 6


def unit_test():
    assert convert_tile_XY_to_LatLon(4, 7, 5) == (55.776573, -22.500000)
    assert convert_tile_XY_to_LatLon(10, 184, 401) == (36.315125, -115.312500)
    assert find_surrounding_tiles(36.159334,-115.152807, 10) == [(10, 183, 400), (10, 183, 401), (10, 183, 402), (10, 184, 400), (10, 184, 401), (10, 184, 402), (10, 185, 400), (10, 185, 401), (10, 185, 402)]

    for zoomLevel in range(0, 20):
        x,y = get_tile_XY(36.159334, -115.152807, zoomLevel)

        s,w,n,e = tile_edges(zoomLevel, x, y)
        print("%d: %7d,%7d --> %1.6f :: %1.6f, %1.6f :: %1.6f" % (zoomLevel, x, y, s, n, w, e))
        print("<img src='%s'><br>" % tile_URL(zoomLevel, x, y, "osm"))


def num_of_tiles(zoomLevel: int) -> int:
    """ Calculate the number of tiles at a given zoom level.
        https://wiki.openstreetmap.org/wiki/Zoom_levels

    Args:
        zoomLevel (int): The zoom level between 0 - 19 using the OpenStreet Map (OSM) 'standard' style

    Returns:
        int: The number of tiles at the given zoom level.
    """
    return pow(2, zoomLevel)


def sec(x: float) -> float:
    """ Calculate the secant of an angle

    Args:
        x (float): The angle in radians.

    Returns:
        float: The secant of the angle.
    """
    return 1 / math.cos(x)


def get_tile_XY(lat: float, lon: float, zoomLevel: int) -> tuple:
    """ Calculate the tile coordinates for a given latitude, longitude, and zoom level.

    Args:
        lat (float): The latitude in degrees
        lon (float): The longitude in degrees
        zoomLevel (int): The zoom level between 0 - 19 for using the OpenStreet Map (OSM) 'standard' style

    Returns:
        tuple: The tile coordinates (x, y), where (0,0) represents the top-left corner of the map.
    """
    n = num_of_tiles(zoomLevel)
    xOffset = (lon + 180) / 360
    yOffset = (1 - math.log(math.tan(math.radians(lat)) + sec(math.radians(lat))) / math.pi) / 2
    x = int(xOffset*n)
    y = int(yOffset*n)

    return (x, y)


def convert_tile_XY_to_LatLon(zoomLevel: int, x: int, y: int) -> tuple:
    """ Convert a tile X & Y  values to the latitude and longitude of the upper left corner of the tile Bounding Box (Bbox)
        https://quad.osm.lol/

    Args:
        zoomLevel (int): The zoom level.
        x (int): The x-coordinate of the tile.
        y (int): The y-coordinate of the tile.

    Returns:
        tuple: The latitude and longitude.
    """
    if x < 0 or y < 0:
        raise ValueError("Both X and yY must be greater than 0")

    n = num_of_tiles(zoomLevel)
    #TODO: Add centerX and centerY calculations
    #centerX = (x + 0.5) / n
    #centerY = (y + 0.5) / n
    # lon = -180.0 + 360.0 * ((x + 0.5) / n)

    upperLeftY = y / n
    upperLeftX = x / n
    lat = convert_mercatorY_to_latitude(math.pi * (1 - 2 * upperLeftY))
    lon =  -180.0 + 360.0 * upperLeftX

    return (round(lat, GPS_DECIMAL_ROUNDING), round(lon, GPS_DECIMAL_ROUNDING))


def lat_edges(zoomLevel: int, y: int) -> tuple:
    """ Calculate the latitude edges of a tile at a given zoom level.

    Args:
        y (int): The y-coordinate of the tile.
        zoomLevel (int): The zoom level.

    Returns:
        tuple: The latitude edges (lat1, lat2), where lat1 is the southern edge and lat2 is the northern edge.
    """
    n = num_of_tiles(zoomLevel)
    unit = 1 / n
    relY1 = y * unit
    relY2 = relY1 + unit
    lat1 = convert_mercatorY_to_latitude(math.pi * (1 - 2 * relY1))
    lat2 = convert_mercatorY_to_latitude(math.pi * (1 - 2 * relY2))

    return (lat1, lat2)


def lon_edges(zoomLevel: int, x: int) -> tuple:
    """ Calculate the longitude edges of a tile at a given zoom level.

    Args:
        x (int): The x-coordinate of the tile.
        zoomLevel (int): The zoom level.

    Returns:
        tuple: The longitude edges (lon1, lon2), where lon1 is the western edge and lon2 is the eastern edge.
    """
    n = num_of_tiles(zoomLevel)
    unit = 360 / n
    lon1 = -180 + x * unit
    lon2 = lon1 + unit

    return (lon1, lon2)


def tile_edges(zoomLevel: int, x:int , y:int) -> tuple:
    """ Calculate the edges of a tile at a given zoom level.

    Args:
        x (int): The x-coordinate of the tile.
        y (int): The y-coordinate of the tile.
        zoomLevel (int): The zoom level.

    Returns:
        tuple: The edges of the tile (lat2, lon1, lat1, lon2), where lat2 is the southern edge, lon1 is the western edge, lat1 is the northern edge, and lon2 is the eastern edge.
    """
    lat1, lat2 = lat_edges(zoomLevel, y)
    lon1, lon2 = lon_edges(zoomLevel, x)

    return (lat2, lon1, lat1, lon2)


def convert_mercatorY_to_latitude(mercatorY: float) -> float:
    """ Convert a Mercator Y coordinate to a latitude.
        https://en.wikipedia.org/wiki/Web_Mercator_projection

    Args:
        mercatorY (float): The Mercator Y coordinate.

    Returns:
        float: The latitude.
    """
    return math.degrees(math.atan(math.sinh(mercatorY)))


def tile_pixel_size() -> int:
    """ Tiles are 256 × 256 pixel PNG files
    """
    return TILE_SIZE


def tile_layer_ext(layer) -> str:
    if layer in 'oam':
        return 'jpg'

    return 'png'


def tile_layer_base_url(layer) -> str:
    layers = { #"tah": "http://cassini.toolserver.org:8080/http://a.tile.openstreetmap.org/+http://toolserver.org/~cmarqu/hill/",
	          "osm": "https://tile.openstreetmap.org/",
              "oam": "http://oam1.hypercube.telascience.org/tiles/1.0.0/openaerialmap-900913/",
              "mapnik": "http://tile.openstreetmap.org/mhapnik/"
           }

    return layers[layer]


def tile_URL(zoomLevel, x, y, layer) -> str:
    return "%s%d/%d/%d.%s" % (tile_layer_base_url(layer), zoomLevel, x, y, tile_layer_ext(layer))


def tileXY_to_quadkey(zoomLevel: int, x: int, y: int) -> str:
    """Convert tile (x, y, zoom) to a Bing-style QuadKey string without bit masking."""
    quadkey = ""
    for i in range(zoomLevel):
        level = zoomLevel - i - 1
        divisor = 2 ** level
        digit = 0

        # Determine which quadrant (0–3) this tile is in at this zoom level using floor division operator
        if x // divisor % 2 == 1:
            digit += 1
        if y // divisor % 2 == 1:
            digit += 2

        quadkey += str(digit)

    return quadkey

def find_surrounding_tiles(lat: float, lon: float, zoomLevel: int) -> list:
    x, y = get_tile_XY(lat, lon, zoomLevel)
    tiles = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            nx = (x + dx)
            ny = y + dy
            tiles.append((zoomLevel, nx, ny))

    return tiles


if __name__ in {"__main__", "__mp_main__"}:
    #unit_test()
    print(tileXY_to_quadkey(16, 11764, 25713))

    # Create a 3×3 grid of tiles centered on CENTER_X, CENTER_Y
    with ui.grid(columns=3).classes('gap-0'):  # remove gaps for seamless tiling
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                x = 94440 + dx
                y = 205593 + dy
                imgURL= tile_URL(16, x, y, "osm")
                print(imgURL)
                ui.image(imgURL).classes('w-64 h-64 object-cover')  # adjust size as needed

    #ui.run()
