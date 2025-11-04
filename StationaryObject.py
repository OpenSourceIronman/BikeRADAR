#!/usr/bin/python3

# Standard libraries
from dataclasses import dataclass, field
import math
from Risk import Risk

@dataclass
class StationaryObject:
    """A stationary object in a polar radar plot."""

    # class variable (shared across all instances)
    objectId: int = field(default=0, init=False, repr=False)

    radius: list[int] = field(default_factory=list)
    theta: list[int] = field(default_factory=list)

    objectPolyline: list[list, list] = field(default_factory=list)

    risk: Risk()

    def add_point(self, radius: int, theta: int):
        """Adds a point to the object's radius and theta lists."""
        self.radius.append(radius)
        self.theta.append(theta)

    def define_object_outer_polyline(self):
        """Defines the outer polyline of the object."""
        self.objectPolyline = [self.radius, self.theta]


    def __str__(self) -> str:
        """Returns a string representation of the object."""

        position = []
        for i, (r, thetaDegrees) in enumerate(zip(self.radius, self.theta)):
            thetaRadians = math.radians(thetaDegrees)
            x = r * math.cos(thetaRadians)
            y = r * math.sin(thetaRadians)

            # Rotate the object by 90 degrees counter-clockwise to match the radar plot in Radar.py file
            xRotated = round(-y, 5)
            yRotated = round(x, 5)

            if xRotated == -0.0:
                xRotated = 0.0

            if yRotated == -0.0:
                yRotated = 0.0

            position.append((xRotated, yRotated))

        return f"StationaryObject #{self.objectId} (X-Y Points: {position} & Polar Points: (Radius={self.radius} , Theta={self.theta})"

if __name__ == "__main__":
    data = []

    pole = StationaryObject()
    pole.add_point(0, 0)
    pole.add_point(1, 90)
    pole.add_point(2, 180)
    pole.add_point(3, 270)
    pole.define_object_outer_polyline()
    data.append(pole)

    print(data[0])
