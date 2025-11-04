#!/usr/bin/python3

# macOS packaging support
#from multiprocessing import freeze_support  # noqa
#freeze_support()                            # noqa

# External libraries
from nicegui import native, ui      # pip install nicegui
import numpy as np                  # pip install numpy
#import threading
import serial                       # pip install pyserial
import math                         # pip install math
import plotly.graph_objects as go   # pip install plotly
import os
from dotenv import load_dotenv

# Internal libraries
from StationaryObject import StationaryObject

speedInMetersPerSecond = 10
pollingRateInHz = 2
objectsFound = 0

class Radar:

    DEBUG_STATEMENTS_ON = False

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
        self.mode = mode

        if mode == "TESTING":
            self.serialConnection = serial.serial_for_url('loop://', timeout=1)
            #threading.Thread(target=Radar.scan(currentPlotContainer), args=(self.serialConnection,), daemon=True).start()
        else:
            try:
                # Initialize production serial connection with USB port at 9600 baud rate
                self.serialConnection = serial.Serial(port, 9600)
            except serial.serialutil.SerialException as e:
                print(f"Error initializing serial connection: {e}")
                ui.notify("ERROR: RADAR module serial port connection failed")
                self.serialConnection = None

        # Max range of the radar in meters
        if maxRadius > 300:
            raise ValueError("Maximum radius cannot exceed 300 meters.")
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


    def polar_to_cartesian(r: int, thetaDegrees: int) -> tuple:
        """ Convert polar coordinates to Cartesian coordinates.

        Args:
            r (int): The radius.
            thetaDegrees (int): The angle in degrees.

        Returns:
            tuple: A tuple containing the x and y coordinates rounded to three decimal places.
        """
        thetaRadians = math.radians(thetaDegrees)
        x = round(r * math.cos(thetaRadians), 3)
        y = round(r * math.sin(thetaRadians), 3)

        return (x, y)


    def find_stationary_points(self, velocity: int, pollRate: int = 2):
        """" Determine if consecutive time slices contain stationary objects.

        Args:
            velocity (int): The velocity of the moving RADAR module moving towards 270 degrees (down in GUI).
            pollRate (int): The rate at which the data is polled in Hertz.
        """

        distanceMoved = velocity * pollRate
        for r1 in range(1, self.maxRadius - distanceMoved):
            for t1 in range(Radar.FULL_CIRCLE):
                x1, y1 = Radar.polar_to_cartesian(r1, t1)
                y2 = y1 - distanceMoved
                r2, t2 = Radar.cartesian_to_polar(x1, y2)

                if self.dataTimeSliceCurrent[r1, t1] and self.dataTimeSlicePast[int(r2), int(t2)]:
                    print(f"(r1={r1}, t1={t1}) -> (r2={int(r2)}, t2={int(t2)}) = (x1={x1}, y2={y2})")
                    self.dataTimeSliceStationary[r1, t1] = True


    def scan(self, currentPlotContainer):
        """

        Args:
            currentPlotContainer (PlotContainer): The current plot container

        Returns:
            None
        """
        global speedInMetersPerSecond, pollingRateInHz

        print("Scanning...")

        self.reset_current_radar_database()

        if self.mode == "TESTING":
            if (Radar.DEBUG_STATEMENTS_ON): print(self.serial_test())
        else:
            #self.generate_random_data(100)
            self.serial_scan_test()
            data = self.serialConnection.read(self.maxRadius * Radar.FULL_CIRCLE)

        i = 0
        for r in range(self.maxRadius):
            for t in range(Radar.FULL_CIRCLE):
                if i >= len(data):
                    break  # prevent index error
                bit = data[i:i+1]
                i += 1
                self.update_radar_database(bit == b'1', r, t, Radar.CURRENT)

        currentPlotContainer.figure = self.GUI("CURRENT")
        currentPlotContainer.update()

        self.stationaryObjects = []
        self.find_stationary_points(speedInMetersPerSecond, pollingRateInHz)
        #print(f"Stationary Data: {self.dataTimeSliceStationary}")
        stationaryGroupedPoints = self.group_points(self.dataTimeSliceStationary)
        groupId = 0
        if len(stationaryGroupedPoints) > 0:
            objectsFoundLabel.set_text(f"Stationary Objects Found: {len(stationaryGroupedPoints)} ........ Group ID Data: {stationaryGroupedPoints}")
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

    def serial_scan_test(self):

        for radius in range(1, self.maxRadius):
            radiusNumOfBytes = self.serialConnection.write(format(radius, '09b').encode()) # 9-bit binary with leading zeros to create b'000000001' to b'100101100' # Radius = 300
            for _ in range(2):
                numOfBytes = [0, 0, 0, 0]
                numOfBytes[0] = self.serialConnection.write(b'111110001010110101010101010101010101010001111')   # 45 bits for 45 degrees = Radar.EIGHTH_CIRCLE
                numOfBytes[1] = self.serialConnection.write(b'111110001010110101010101010101010101010001111')   # 45 bits for 45 degrees = Radar.EIGHTH_CIRCLE
                numOfBytes[2] = self.serialConnection.write(b'111110001010110101010101010101010101010001111')   # 45 bits for 45 degrees = Radar.EIGHTH_CIRCLE
                numOfBytes[3] = self.serialConnection.write(b'111110001010110101010101010101010101010001111')   # 45 bits for 45 degrees = Radar.EIGHTH_CIRCLE

        for radius in range(1, self.maxRadius):
            radiusNumOfBytes = self.serialConnection.read(radiusNumOfBytes)
            if sum(numOfBytes) == Radar.FULL_CIRCLE:
                thetaBinary = self.serialConnection.read(Radar.FULL_CIRCLE)
                return thetaBinary
            else:
                raise ValueError("Invalid number of bytes received")


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
        """ Reset the current time slice RADAR Numpy array to False

        """
        self.dataTimeSliceCurrent = np.zeros((self.maxRadius, Radar.FULL_CIRCLE), dtype=bool)


    def update_radar_database(self, data: bool, r: int, theta: int, timeSlice):
        """ Update the RADAR Numpy array with new data.

        Args:
            data (bool): True if RADAR object is present, False otherwise
            r (int): Radius coordinate (in meters) to update
            theta (int): Angle coordinate (in degrees) to update
            timeSlice: The time slice to update
        """
        if timeSlice == Radar.PAST:
            self.dataTimeSlicePast[r, theta] = data
        elif timeSlice == Radar.CURRENT:
            self.dataTimeSliceCurrent[r, theta] = data
        elif timeSlice == Radar.NEXT:
            self.dataTimeSliceNext[r, theta] = data
        else:
            raise ValueError("Invalid time slice")


    def generate_random_data(self, numOfPoints, thetaMax: int = FULL_CIRCLE):
        """ Generate random data for the current time slice.

        Args:
            numOfPoints (int): The number of points to generate.
            thetaMax (int): The maximum angle coordinate (in degrees).
        """
        for _ in range(numOfPoints):
            self.update_radar_database(True, np.random.randint(1, self.maxRadius), np.random.randint(0, Radar.FULL_CIRCLE), Radar.CURRENT)


    def manual_update(self):
        self.update_radar_database(True, 60, 0, Radar.PAST)
        self.update_radar_database(True, 60, 3, Radar.PAST)
        self.update_radar_database(True, 40, 0, Radar.CURRENT)
        self.update_radar_database(True, 40, 3, Radar.CURRENT)
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

        for r in range(self.maxRadius):
            for t in range(Radar.FULL_CIRCLE):
                if data[r, t]:
                    radiusPlotPoints.append(r)
                    thetaPlotPoints.append(t)

        return radiusPlotPoints, thetaPlotPoints


    def GUI(self, timeSlice: str):
        """ Create a Plotly figure for the GUI using input RADAR.py object data.

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
                #angularaxis=dict(rotation=90, direction="clockwise")  # Set numbering direction to clockwise like a compass and rotate 90 degree counterclockwise
            ),
            font=dict(color="white")
        )

        return figure


    def toggle_GUI(value: str):
        """ Toggle the visibility of the GUI plots based on the time slice selected via Radio Button.

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

    EP3 = Radar(300, '/dev/ttyUSB0', 'PRODUCTION')
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
        objectsFoundLabel = ui.label("Stationary Objects Found: 0")

    load_dotenv()
    onAirKey = os.getenv("ON_AIR_TOKEN")
    ui.run(native=True, dark=True, window_size=(660, 800), title='RADAR Data', on_air=onAirKey) #, reload=False, port=native.find_open_port())
