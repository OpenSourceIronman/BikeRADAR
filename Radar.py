#!/usr/bin/python3

# External libraries
from nicegui import Tailwind, ui
import numpy as np
#import serial
import math
import plotly.graph_objects as go
from collections import defaultdict, deque

from StationaryObject import StationaryObject

PAST = 0
CURRENT = 1
NEXT = 2

RADIUS = 0
THETA = 1
GROUP_ID = 2

FULL_CIRCLE = 360

class Radar:
    def __init__(self, maxRadius: int = 300, port: str = '/dev/ttyUSB0'):
        #self.serialConnection = serial.Serial(port, 9600)

        #
        self.maxRadius = maxRadius

        # Create a 2D array (len(radius) x len(theta)) filled with zeros
        self.dataTimeSlicePast = np.zeros((maxRadius, FULL_CIRCLE), dtype=bool)
        self.dataTimeSliceCurrent = np.zeros((maxRadius, FULL_CIRCLE), dtype=bool)
        self.dataTimeSliceNext = np.zeros((maxRadius, FULL_CIRCLE), dtype=bool)

        # Uses StationaryObject Dataclass
        self.stationaryObjects = []

    def __str__(self):
        return f"RadarPlot(dataTimeSlicePast={self.dataTimeSlicePast}, dataTimeSliceCurrent={self.dataTimeSliceCurrent}, dataTimeSliceNext={self.dataTimeSliceNext}, stationaryObjects={self.stationaryObjects})"

    def get_points(self):
        """
        Returns a list of points representing radar plot points.

        Each point is a list of (radius, theta, group_id).
        Grouping algorithm only works because dataTimeSliceCurrent is built scanining theta from 0 to 259 before incrementing radius by one
        """

        points = []
        groupId = 0

        for r in range(self.maxRadius):
            for t in range(FULL_CIRCLE):
                if self.dataTimeSliceCurrent[r, t]:
                    points.append([r, t, groupId])

        # Group points by adjacency
        for i in range(1, len(points)):
            prev = points[i-1]
            curr = points[i]

            # Check adjacency by theta or radius
            if (0 <= abs(prev[THETA] - curr[THETA]) <= 1 or abs(prev[THETA] - curr[THETA]) == FULL_CIRCLE - 1) and abs(prev[RADIUS] - curr[RADIUS]) <= 1:
                curr[GROUP_ID] = prev[GROUP_ID]
            else:
                groupId += 1
                curr[GROUP_ID] = groupId

        return points

    def cartesian_time_slice():
        pass

    def cartesian_to_polar(x, y):
        r = math.sqrt(x**2 + y**2)
        theta = math.degrees(math.atan2(y, x))
        return (r, theta)

    def polar_to_cartesian(r, thetaDegrees):
        thetaRadians = math.radians(thetaDegrees)
        x = r * math.cos(thetaRadians)
        y = r * math.sin(thetaRadians)
        return (x, y)

    def update_group_id(self):
        points = self.find_points()

        for i in range(len(points)):
            if points[i][THETA] == 359:
                pass

    def group_points_CHATGPT(self):
        points = self.get_points()
        print(points)

        points_by_obj = defaultdict(list)
        for r, theta, obj in points:
            points_by_obj[obj].append((r, theta, obj))
        print(points_by_obj)


        clusters = []
        new_group_counter = 0

        for obj, pts in points_by_obj.items():
            print(f"pts: {pts} & Obj: {obj}")
            visited = [False] * len(pts)
            for i, point in enumerate(pts):
                if visited[i]:
                    continue

                cluster = []
                queue = deque([i])
                visited[i] = True

                while queue:
                    j = queue.popleft()
                    cluster.append(pts[j])
                    rj, thetaj, _ = pts[j]
                    for k, (rk, thetak, _) in enumerate(pts):
                        if not visited[k]:
                            if abs(rj - rk) <= 1 or abs(thetaj - thetak) <= 1:
                                visited[k] = True
                                queue.append(k)

                # Decide objectId for this cluster
                if len(cluster) == 1:
                    # Create a new label (C, D, etc.)
                    new_group_counter += 1
                    new_id = chr(ord('C') + new_group_counter - 1)
                    cluster = [(r, t, new_id) for (r, t, _) in cluster]
                else:
                    cluster = [(r, t, obj) for (r, t, _) in cluster]

                clusters.append(cluster)

        return clusters


    def find_stationary_points(self, velocity: int, pollRate: int = 2):
        """" Determine if consecutive time slices contain stationary objects.

        Args:
            velocity (int): The velocity of the moving RADAR module
            pollRate (int): The rate at which the data is polled in Hertz
        """
        stationaryObjects = []
        for r in range(self.maxRadius):
            for t in range(FULL_CIRCLE):
                radiusMoved = velocity * pollRate
                if self.dataTimeSliceCurrent[r, t] == self.dataTimeSlicePast[(r+radiusMoved), t]:
                    obj = StationaryObject
                    obj.add_point(r, t)
                    stationaryObjects.append(obj)

        return stationaryObjects

    def scan(self):
        for r in range(self.maxRadius):
            for t in range(FULL_CIRCLE):
                data = self.serialConnection.read()
                if data == b'1':
                    self.update_radar(True, r, t)
                else:
                    self.update_radar(False, r, t)

    def next_scan(self):
        self.dataTimeSlicePast = self.dataTimeSliceCurrent
        self.dataTimeSliceCurrent = self.scan()


    def update_radar(self, data: bool, r: int, theta: int, timeSlice):
        if timeSlice == PAST:
            self.dataTimeSlicePast[r, theta] = data
        elif timeSlice == CURRENT:
            self.dataTimeSliceCurrent[r, theta] = data
        elif timeSlice == NEXT:
            self.dataTimeSliceNext[r, theta] = data
        else:
            raise ValueError("Invalid time slice")

    def create_plot_points(self, data):
        radiusPlotPoints = []
        thetaPlotPoints = []

        for r in range(self.maxRadius):
            for t in range(FULL_CIRCLE):
                if data[r, t]:
                    radiusPlotPoints.append(r)
                    thetaPlotPoints.append(t)

        return radiusPlotPoints, thetaPlotPoints


if __name__ in {"__main__", "__mp_main__"}:

    EP3 = Radar()
    EP3.update_radar(True, 60, 0, PAST)
    EP3.update_radar(True, 50, 0, CURRENT)
    EP3.update_radar(True, 100, 0, CURRENT)
    EP3.update_radar(True, 100, 1, CURRENT)
    EP3.update_radar(True, 100, 2, CURRENT)
    EP3.update_radar(True, 100, 3, CURRENT)
    EP3.update_radar(True, 101, 3, CURRENT)
    EP3.update_radar(True, 102, 4, CURRENT)
    EP3.update_radar(True, 108, 5, CURRENT)
    EP3.update_radar(True, 103, 4, CURRENT)
    EP3.update_radar(True, 40, 0, NEXT)
    #stationaryObjects = EP3.find_stationary_points(10, 2)
    print(EP3.get_points())

    #print(EP3)

    radius, theta = EP3.create_plot_points(EP3.dataTimeSliceCurrent)


    fig = go.Figure(go.Scatterpolar(r= radius, theta= theta,
        mode="markers",
        marker=dict(size=4, color="red"),
        name="Detection"))

    fig.update_layout(
        margin=dict(l=60, r=60, t=30, b=30),
        paper_bgcolor="#4d4d4d",
        plot_bgcolor="#4d4d4d",
        polar=dict(
            bgcolor="#4d4d4d",
            radialaxis=dict(visible=True, range=[0, 300], tickvals=[100, 200]),
            angularaxis=dict(rotation=90, direction="clockwise",)   # rotate CCW
        ),
        font=dict(color="white"),
        #showlegend=True
    )

    plot = ui.plotly(fig).classes('justify-center w-full h-[500px]')
    ui.button("Perform new RADAR scan", icon='radar', on_click= lambda: EP3.next_scan()).props('color=orange').classes('justify-center w-full')
    with ui.row().classes('items-center'):
        ui.label("Time Slice:")
        radioTimeSliceInput = ui.radio(["PAST", "CURRENT"], value="PAST").props('inline')

    ui.run(native=True, dark=True, window_size=(720, 720), title='RADAR Data', on_air=None)
