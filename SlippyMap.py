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

# 3rd party libraries
from PIL import Image, ImageDraw  # pip install Pillow
import requests
from io import BytesIO

IN = 1
OUT = -1
TILE_SIZE = 256
GPS_DECIMAL_ROUNDING = 6

mapCenter = (36.149727, -115.334172)
currentZoomLevel = 8

def unit_test():
    assert tileXY_to_quadkey(16, 11772, 25701) == "0230130113311302"
    assert convert_tile_XY_to_LatLon(4, 7, 5) == (55.776573, -22.500000)
    assert convert_tile_XY_to_LatLon(10, 184, 401) == (36.315125, -115.312500)
    assert find_surrounding_tiles(36.159334,-115.152807, 10) == [(10, 183, 400), (10, 183, 401), (10, 183, 402), (10, 184, 400), (10, 184, 401), (10, 184, 402), (10, 185, 400), (10, 185, 401), (10, 185, 402)]

    for zoomLevel in range(0, 20):
        x,y = get_tile_XY(zoomLevel, 36.159334, -115.152807)

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


def get_tile_XY(zoomLevel: int, lat: float, lon: float) -> tuple:
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
    """ Convert tile (x, y, zoom) to a Bing-style QuadKey string
        Top-left → 0
        Top-right → 1
        Bottom-left → 2
        Bottom-right → 3
    """
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
    x, y = get_tile_XY(zoomLevel, lat, lon)
    tiles = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            nx = (x + dx)
            ny = y + dy
            tiles.append((zoomLevel, nx, ny))

    return tiles

def zoom_tiles():
    x, y = get_tile_XY(zoomLevel, lat, lon)
    return (zoomLevel + 1, x * 2, y * 2) if zoomLevel < 16 else zoomLevel

    x, y = get_tile_XY(zoomLevel, lat, lon)
    return (zoomLevel - 1, x // 2, y // 2) if zoomLevel > 0 else zoomLevel


def update_on_zoom(mapCenter, buttonClicked: bool = False):
    if currentZoomLevel < 10:
       currentZoomLevelText =  "0" + str(currentZoomLevel)
    else:
        currentZoomLevelText = str(currentZoomLevel)

    zoomLabel.text = f"Zoom Level: {currentZoomLevelText}"

    if buttonClicked:
        mapGrid.clear()
        tileX, tileY = get_tile_XY(currentZoomLevel, mapCenter[0], mapCenter[1])
        with mapGrid:
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    x = tileX + dx
                    y = tileY + dy
                    imgURL= tile_URL(currentZoomLevel, x, y, "osm")                   #print(imgURL)
                    ui.image(imgURL).classes('w-64 h-64')  # adjust size as needed


    #mapGrid.add_child(ui.image(tile_URL(currentZoomLevel, tileX, tileY, "osm")).classes('w-64 h-64 object-cover'))

def zoom_in(zoomLevel: int) -> int:
    return (zoomLevel + 1) if zoomLevel < 16 else zoomLevel

def zoom_out(zoomLevel: int) -> int:
    return (zoomLevel - 1) if zoomLevel > 0 else zoomLevel

def on_zoom_button_click(direction):
    global currentZoomLevel, mapCenter

    if direction == IN:
        currentZoomLevel = zoom_in(currentZoomLevel)
    elif direction == OUT:
        currentZoomLevel = zoom_out(currentZoomLevel)

    update_on_zoom(mapCenter, True)




def draw_line_on_map_tile(zoomLevel: int, x: int, y: int, lineStart: tuple, lineEnd: tuple, color: str = 'blue', width: int = 5):
    base = Image.open(BytesIO(requests.get(tile_URL(zoomLevel, x, y, "osm")).content))
    draw = ImageDraw.Draw(base)
    draw.line((lineStart[0], lineStart[1], lineEnd[0], lineEnd[1]), fill=color, width=width)
    base.save('overlayed.png')

    return filename


if __name__ in {"__main__", "__mp_main__"}:
    #unit_test()
    tileX, tileY = get_tile_XY(currentZoomLevel, mapCenter[0], mapCenter[1])

    # Create a 3×3 grid of tiles centered on tileX, tileY and gaps removed for seamless tiling
    with ui.grid(columns=3).classes('gap-0') as mapGrid:
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                x = tileX + dx
                y = tileY + dy
                imgURL= tile_URL(currentZoomLevel, x, y, "osm")                   #print(imgURL)
                ui.image(imgURL).classes('w-64 h-64')  # adjust size as needed

    with ui.row().classes('justify-center w-full'):
        ui.button("ZOOM IN", on_click=lambda e:on_zoom_button_click(IN)).classes('w-1/3')
        ui.button("ZOOM OUT", on_click=lambda e:on_zoom_button_click(OUT)).classes('w-1/3')
        zoomLabel = ui.label(f"Zoom Level: {currentZoomLevel}").style('margin-top: 7px;')

    update_on_zoom(mapCenter)
    ui.run(title='Slippy Map Test', native=True, dark=True, window_size=(tile_pixel_size()*3.1, tile_pixel_size()*4))
