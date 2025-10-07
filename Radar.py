#!/usr/bin/python3

# External libraries
from nicegui import ui              # pip install nicegui
import numpy as np                  # pip install numpy
import serial                       # pip install pyserial
import math                         # pip install math
import plotly.graph_objects as go   # pip install plotly

# Internal libraries
from StationaryObject import StationaryObject

speedInMetersPerSecond = 10
pollingRateInHz = 2

class Radar:

    PAST = 0
    CURRENT = 1
    NEXT = 2

    RADIUS = 0
    THETA = 1
    GROUP_ID = 2

    FULL_CIRCLE = 360
    QUARTER_CIRCLE = int(FULL_CIRCLE / 4)
    EIGHTH_CIRCLE = int(FULL_CIRCLE / 8)

    def __init__(self, maxRadius: int = 300, port: str = '/dev/ttyUSB0', mode: str = 'TESTING'):
        """Initialize the Radar object.

        Args:
            maxRadius (int, optional): Maximum range of the RADAR in meters. Defaults to 300.
            port (str, optional): Serial port for communication. Defaults to '/dev/ttyUSB0'.
            mode (str, optional): Operating mode ('TESTING' or 'PRODUCTION'). Defaults to 'TESTING'.
        """

        if mode == "TESTING":
            self.mode = mode
            self.serialConnection = serial.serial_for_url('loop://', timeout=1)
        else:
            # Initialize production serial connection with USB port at 9600 baud rate
            self.serialConnection = serial.Serial(port, 9600)

        # Max range of the radar in meters
        self.maxRadius = maxRadius

        # Create a 2D array (len(radius) x len(theta)) filled with False
        self.dataTimeSlicePast = np.zeros((maxRadius, Radar.FULL_CIRCLE), dtype=bool)
        self.dataTimeSliceCurrent = np.zeros((maxRadius, Radar.FULL_CIRCLE), dtype=bool)
        self.dataTimeSliceStationary = np.zeros((maxRadius, Radar.FULL_CIRCLE), dtype=bool)

        # Uses StationaryObject Dataclass
        self.stationaryObjects = []


    def __str__(self):
        return f"RadarPlot(dataTimeSlicePast={self.dataTimeSlicePast}, dataTimeSliceCurrent={self.dataTimeSliceCurrent}, dataTimeSliceNext={self.dataTimeSliceNext}, stationaryObjects={self.stationaryObjects})"


    def group_points(self, dataTimeSlice):
        """ Group points by adjacency and add a group ID for all touch points.

        Each point is a list of (radius, theta, group_id).
        Grouping algorithm only works because dataTimeSliceCurrent is built scanining theta from 0 to 259 before incrementing radius by one
        """

        points = []
        pointsSortedByRadius = []
        pointsSortedByTheta = []
        groupId = 0

        # Get points from current data time slice with group ID set to 0
        for r in range(self.maxRadius):
            for t in range(Radar.FULL_CIRCLE):
                if dataTimeSlice[r, t]:
                    points.append([r, t, groupId])  # Sort by radius

        #print(f"Raw Data: {points}")

        # Group points by adjacency
        for i in range(1, len(points)):
            prev = points[i-1]
            curr = points[i]

            # Check adjacency by theta or radius
            if (0 <= abs(prev[Radar.THETA] - curr[Radar.THETA]) <= 1 or abs(prev[Radar.THETA] - curr[Radar.THETA]) == Radar.FULL_CIRCLE - 1) and abs(prev[Radar.RADIUS] - curr[Radar.RADIUS]) <= 1:
                curr[Radar.GROUP_ID] = prev[Radar.GROUP_ID]
            else:
                groupId += 1
                curr[Radar.GROUP_ID] = groupId

        pointsSortedByRadius = sorted(points, key=lambda x: x[Radar.RADIUS])
        pointsSortedByTheta = sorted(points, key=lambda x: x[Radar.THETA])

        #print(pointsSortedByRadius)
        #print(pointsSortedByTheta)

        # Group points by adjacency
        for i in range(1, len(pointsSortedByTheta)):
            prev = pointsSortedByTheta[i-1]
            curr = pointsSortedByTheta[i]

            # Check adjacency by theta or radius
            if abs(prev[Radar.RADIUS] - curr[Radar.RADIUS]) <= 1 and abs(prev[Radar.THETA] - curr[Radar.THETA]) <= 1:
                curr[Radar.GROUP_ID] = prev[Radar.GROUP_ID]
            else:
                pass

        finalGroupedPoints = sorted(pointsSortedByTheta, key=lambda x: x[Radar.GROUP_ID])
        #print(f"Final Grouping: {finalGroupedPoints}")
        print(f"Number of groups: {len(set(point[Radar.GROUP_ID] for point in finalGroupedPoints))}")

        return finalGroupedPoints


    def cartesian_to_polar(x, y):
        """ Convert Cartesian coordinates to polar coordinates.

        Args:
            x (float): The x-coordinate.
            y (float): The y-coordinate.

        Returns:
            tuple: A tuple containing the radius and angle in degrees.
        """
        r = math.sqrt(x**2 + y**2)
        theta = math.degrees(math.atan2(y, x))
        return (r, theta)


    def polar_to_cartesian(r, thetaDegrees):
        """ Convert polar coordinates to Cartesian coordinates.

        Args:
            r (float): The radius.
            thetaDegrees (float): The angle in degrees.

        Returns:
            tuple: A tuple containing the x and y coordinates.
        """
        thetaRadians = math.radians(thetaDegrees)
        x = r * math.cos(thetaRadians)
        y = r * math.sin(thetaRadians)
        return (x, y)


    def find_stationary_points(self, velocity: int, pollRate: int = 2):
        """" Determine if consecutive time slices contain stationary objects.

        Args:
            velocity (int): The velocity of the moving RADAR module
            pollRate (int): The rate at which the data is polled in Hertz
        """

        radiusMoved = velocity * pollRate
        for r in range(1, self.maxRadius - radiusMoved):
            for t in range(Radar.FULL_CIRCLE):
                if self.dataTimeSliceCurrent[r, t] and self.dataTimeSlicePast[(r+radiusMoved), t]:
                    self.dataTimeSliceStationary[r, t] = True



    def scan(self, currentPlotContainer):
        global speedInMetersPerSecond, pollingRateInHz

        print("Scanning...")

        self.reset_current_radar_database()

        if self.mode == "TESTING":
            #self.generate_random_data(100)
            self.manual_update()
            self.serialConnection.write(b'1_1111_0001_0101_1010_1010_1010_1010_1010_1010_1000_1111')   # 45 bits for 45 degrees = Radar.EIGHTH_CIRCLE
            data = self.serialConnection.read(Radar.EIGHTH_CIRCLE)
            dataStr = data.decode('utf-8').replace('_', '')
            binary = bin(int(dataStr))
            print(f"Data: {data} = {binary})")
        else:
            self.generate_random_data(100)
            #data = self.serialConnection.read(Radar.FULL_CIRCLE)

        #i = 0
        #for r in range(self.maxRadius):
        #    for t in range(Radar.FULL_CIRCLE):
        #        bit = data[i:i+1]
        #        #print(bit)
        #        if bit:
        #            self.update_radar_database(True, r, t, Radar.CURRENT)
        #        else:
        #            self.update_radar_database(False, r, t, Radar.CURRENT)

        currentPlotContainer.figure = self.GUI("CURRENT")
        currentPlotContainer.update()

        self.stationaryObjects = []
        self.find_stationary_points(speedInMetersPerSecond, pollingRateInHz)
        #print(f"Stationary Data: {self.dataTimeSliceStationary}")
        stationaryGroupedPoints = self.group_points(self.dataTimeSliceStationary)
        print(f"Group ID Data: {stationaryGroupedPoints}")
        groupId = 0
        if len(stationaryGroupedPoints) > 0:
            for i in range(stationaryGroupedPoints[-1][Radar.GROUP_ID]+1):
                obj = StationaryObject()
                for point in stationaryGroupedPoints:
                    if point[Radar.GROUP_ID] == groupId:
                        obj.add_point(point[Radar.RADIUS], point[Radar.THETA])
                obj.define_object_outer_polyline()
                groupId += 1
                self.stationaryObjects.append(obj)

        print("Stationary Objects:", self.stationaryObjects)
        stationaryPlotContainer.figure = self.GUI("STATIONARY OBJECTS")
        stationaryPlotContainer.update()


    def next_scan(self, currentPlotContainer, pastPlotContainer):
        """ Lambda function to update the plot containers with new Plotly figures based on the current and past RADAR data.

        Args:
            currentPlotContainer (PlotContainer): The container for the current plot.
            pastPlotContainer (PlotContainer): The container for the past plot.
        """
        self.dataTimeSlicePast = self.dataTimeSliceCurrent.copy()
        pastPlotContainer.figure = self.GUI("PAST")
        pastPlotContainer.update()

        self.scan(currentPlotContainer)


    def reset_current_radar_database(self):
        """ Reset the current RADAR database."""
        self.dataTimeSliceCurrent = np.zeros((self.maxRadius, Radar.FULL_CIRCLE), dtype=bool)


    def update_radar_database(self, data: bool, r: int, theta: int, timeSlice):
        """ Update the RADAR database with new data.

        Args:
            data (bool): The new data to be stored.
            r (int): The radius coordinate.
            theta (int): The angle coordinate.
            timeSlice (int): The time slice to update.
        """
        if timeSlice == Radar.PAST:
            self.dataTimeSlicePast[r, theta] = data
        elif timeSlice == Radar.CURRENT:
            self.dataTimeSliceCurrent[r, theta] = data
        elif timeSlice == Radar.NEXT:
            self.dataTimeSliceNext[r, theta] = data
        else:
            raise ValueError("Invalid time slice")


    def generate_random_data(self, numOfPoints, theta: int = FULL_CIRCLE):
        """Generate random data for the radar.

        Args:
            numOfPoints (int): The number of points to generate.
            thetaMax (int): The maxium angle coordinate.
        """
        for _ in range(numOfPoints):
            self.update_radar_database(True, np.random.randint(1, self.maxRadius), np.random.randint(0, Radar.FULL_CIRCLE), Radar.CURRENT)


    def manual_update(self):
        self.update_radar_database(True, 60, 0, Radar.PAST)
        self.update_radar_database(True, 40, 0, Radar.CURRENT)
        self.update_radar_database(True, 80, 0, Radar.CURRENT)
        self.update_radar_database(True, 100, 359, Radar.CURRENT)
        self.update_radar_database(True, 100, 1, Radar.CURRENT)
        self.update_radar_database(True, 100, 2, Radar.CURRENT)
        self.update_radar_database(True, 100, 3, Radar.CURRENT)
        self.update_radar_database(True, 101, 3, Radar.CURRENT)
        self.update_radar_database(True, 102, 4, Radar.CURRENT)
        self.update_radar_database(True, 108, 5, Radar.CURRENT)
        self.update_radar_database(True, 103, 4, Radar.CURRENT)


    def create_plot_points(self, data):
        """ Create plot points for the GUI graph using input RADAR data.

        Args:
            data (numpy.ndarray): The radar data.

        Returns:
            tuple: A tuple containing the radius plot points and theta plot points.
        """
        radiusPlotPoints = []
        thetaPlotPoints = []

        #dataGrouped = self.group_points(data)
        #print(f"Data with Grouped Points: {dataGrouped}")

        for r in range(self.maxRadius):
            for t in range(Radar.FULL_CIRCLE):
                if data[r, t]:
                    radiusPlotPoints.append(r)
                    thetaPlotPoints.append(t)

        return radiusPlotPoints, thetaPlotPoints


    def GUI(self, timeSlice: str):
        """Create a Plotly figure for the GUI using input RADAR data.

        Args:
            timeSlice (str): The time slice to display.

        Returns:
            go.Figure: The Plotly figure.
        """

        if timeSlice == "CURRENT":
            radiusList, thetaList = self.create_plot_points(self.dataTimeSliceCurrent)
        elif timeSlice == "PAST":
            radiusList, thetaList = self.create_plot_points(self.dataTimeSlicePast)
        elif timeSlice == "STATIONARY OBJECTS":
            radiusList, thetaList = self.create_plot_points(self.dataTimeSliceStationary)
        else:
            raise ValueError("Invalid time slice")


        figure = go.Figure(go.Scatterpolar(r= radiusList, theta= thetaList,
            mode="markers",
            marker=dict(size=4, color="red"),
            name="Detection"))

        figure.update_layout(
            margin=dict(l=30, r=30, t=30, b=30),
            paper_bgcolor="#4d4d4d",
            plot_bgcolor="#4d4d4d",
            polar=dict(
                bgcolor="#4d4d4d",
                radialaxis=dict(visible=True, range=[0, self.maxRadius], tickvals=[100, 200]),
                angularaxis=dict(rotation=90, direction="clockwise")  # Set numbering direction to clockwise like a compass and rotate 90 degree counterclockwise
            ),
            font=dict(color="white")
        )

        return figure


    def toggle_GUI(value):
        """ Toggle the visibility of the GUI plots based on the selected time slice.

        Args:
            value (str): The selected time slice ("CURRENT", "PAST", or "STATIONARY OBJECTS").
        """
        if value == "CURRENT":
            pastPlotContainer.visible = False
            stationaryPlotContainer.visible = False
            currentPlotContainer.visible = True
        elif value == "PAST":
            currentPlotContainer.visible = False
            stationaryPlotContainer.visible = False
            pastPlotContainer.visible = True
        elif value == "STATIONARY OBJECTS":
            currentPlotContainer.visible = False
            pastPlotContainer.visible = False
            stationaryPlotContainer.visible = True
        else:
            raise ValueError("DEV ERROR: Invalid time slice radio button selected!")


if __name__ in {"__main__", "__mp_main__"}:

    EP3 = Radar(300, '/dev/ttyUSB0', 'TESTING')
    #EP3.generate_random_data(100)
    EP3.manual_update()

    with ui.row().classes('justify-center w-full'):
        currentPlotContainer = ui.plotly(EP3.GUI("CURRENT")).classes('w-[600px] h-[525px]')
        pastPlotContainer = ui.plotly(EP3.GUI("PAST")).classes('w-[600px] h-[525px]')
        stationaryPlotContainer = ui.plotly(EP3.GUI("STATIONARY OBJECTS")).classes('w-[600px] h-[525px]')
        pastPlotContainer.visible = False
        stationaryPlotContainer.visible = False

    ui.button("PERFORM NEW RADAR SCAN", icon='radar', on_click= lambda: EP3.next_scan(currentPlotContainer, pastPlotContainer)).props('color=orange').classes('justify-center w-full')
    with ui.row().classes('items-center'):
        ui.label("RADAR Time Slice:")
        radioTimeSliceInput = ui.radio(["CURRENT", "PAST", "STATIONARY OBJECTS"], value="CURRENT", on_change= lambda e: Radar.toggle_GUI(e.value)).props('inline').classes('mr-2')

    ui.run(native=True, dark=True, window_size=(660, 720), title='RADAR Data', on_air=None)
