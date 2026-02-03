#!/usr/bin/python3

# Standard library imports not needing pip installs
import uuid
import random
import asyncio
import math

# Third-party library imports
import zmq
import zmq.asyncio

class Risk:

    LOW = 1
    MEDIUM = 2
    HIGH = 3

    FRONT = 0
    RIGHT = 1
    BACK = 2
    LEFT = 3

    OPEN = 2
    CLOSED = 1
    ARCHIVED = 0

    def main():
        print(Risk.convert_lat_long_to_tile_id(36.19542, -115.19521, 14))
        print(Risk.convert_tile_id_to_lat_long(36.232798, 103246, 18))

        risks = []
        for _ in range(10):
            risks.append(Risk(random.randint(1, 3), random.randint(0, 2)))

        print(risks[0])
        risks[0].set_risk_direction(Risk.FRONT)
        risks[0].set_risk_status(Risk.CLOSED)
        risks[0].set_risk_severity(1)
        print(risks[0])

        #print(random.choice(["Open", "Closed", "ARCHIVED"]))


    def __init__(self, severity: int = LOW, status: int = OPEN):
        self.id = uuid.uuid4()
        self.severity = severity
        self.direction = None
        self.mapTitleId = None
        self.status = status


    def __str__(self):
        """ Returns a string representation of a risk object using global constants.

        Returns:
            str: A string representation of the risk object.
        """
        statusStr = ""
        match self.status:
            case Risk.OPEN:
                statusStr = "OPEN"
            case Risk.CLOSED:
                statusStr = "CLOSED"
            case Risk.ARCHIVED:
                statusStr = "ARCHIVED"

        match self.direction:
            case Risk.FRONT:
                directionStr = "FRONT"
            case Risk.BACK:
                directionStr = "BACK"
            case Risk.LEFT:
                directionStr = "LEFT"
            case Risk.RIGHT:
                directionStr = "RIGHT"
            case _:
                directionStr = "UNKNOWN"

        return f"{directionStr} risk with id={self.id}, severity={self.severity}, and status={statusStr}"


    def __repr__(self):
        return f"Risk(id={self.id}, severity={self.severity}, status={self.status})"


    def __eq__(self, other):
        return self.severity == other.severity and self.status == other.status and self.direction == other.direction


    def __ge__(self, other):
        return self.severity >= other.severity


    def __le__(self, other):
        return self.severity <= other.severity


    def __gt__(self, other):
        return self.severity > other.severity


    def __lt__(self, other):
        return self.severity < other.severity


    def __hash__(self):
        return hash((self.id, self.severity, self.status, self.direction))

    def set_map_title_id(self, mapId: str):
        """ Sets the map title id based on GPS coordinates of a risk object
            https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Tools
            https://help.openstreetmap.org/questions/40163/where-can-i-find-out-tiles-number/
            https://mc.bbbike.org/mc/?lon=51.5273&lat=25.2806&zoom=14&num=1&mt0=mapnik

        Args:
            mapId (str): The new map title id to set.
        """
        self.mapTitleId = mapId

    def convert_lat_long_to_tile_id(lat: float, lon: float, zoom: int):
        n = 2 ** zoom
        latRad = math.radians(lat)
        xTile = int((lon + 180.0) / 360.0 * n)
        yTile = int((1.0 - math.asinh(math.tan(latRad)) / math.pi) / 2.0 * n)

        return xTile, yTile


    def convert_tile_id_to_lat_long(xTile: int, yTile: int, zoom: int):
        n = 2 ** zoom
        lon = xTile / n * 360.0 - 180.0
        latRad = math.atan(math.sinh(math.pi * (1 - 2 * yTile / n)))
        lat = math.degrees(latRad)

        return lat, lon

    def set_risk_direction(self, newDirection: int):
        """ Sets the direction that a risk object is approaching model from

        Args:
            newDirection (int): The new direction to set.
        """
        match newDirection:
            case Risk.FRONT:
                self.direction = Risk.FRONT
            case Risk.RIGHT:
                self.direction = Risk.RIGHT
            case Risk.BACK:
                self.direction = Risk.BACK
            case Risk.LEFT:
                self.direction = Risk.LEFT
            case _:
                raise ValueError(f"{newDirection} is an invalid risk direction")


    def define_mqtt_topic(self):
        """ Defines the MQTT topic for the risk object.

        Args:
            None
        """
        global context, socket

        context = zmq.asyncio.Context()
        socket = context.socket(zmq.PUSH)
        socket.bind('tcp://localhost:5555')

        topic = f"tile/{self.id}"
        return topic


    def define_mqtt_payload(self):
        """ Defines the MQTT payload for the risk object.

        Args:
            None
        """
        pass

    async def mqtt_publish(self):
        """ Publishes the risk object to the MQTT broker.

        Args:
            None
        """
        asyncio.run(send_loop())


    def set_risk_status(self, newStatus: int):
        """ Sets the processing status of a risk object.

        Args:
            newStatus (int): The new processing status to set.
        """
        match newStatus:
            case Risk.OPEN:
                self.status = Risk.OPEN
            case Risk.CLOSED:
                self.status = Risk.CLOSED
            case Risk.ARCHIVED:
                self.status = Risk.ARCHIVED
            case _:
                raise ValueError(f"{newStatus} is an invalid risk status")


    def set_risk_severity(self, newSeverity: int):
        """ Sets the severity (possible danger level / potential impact) of a risk object, with higher severity indicating greater danger.

        Args:
            newSeverity (int): The new severity to set.
        """
        if newSeverity < Risk.LOW or newSeverity > Risk.HIGH:
            raise ValueError(f"{newSeverity} is an invalid risk severity")
        else:
            self.severity = newSeverity

    def unit_test():
        risk = Risk()
        risk.set_risk_direction(Risk.FRONT)
        risk.set_risk_status(Risk.OPEN)
        risk.set_risk_severity(Risk.MEDIUM)
        assert risk.direction == Risk.FRONT
        assert risk.status == Risk.OPEN
        assert risk.severity == Risk.MEDIUM
        print("All tests passed!")


if __name__ == "__main__":
    Risk.main()
    #Risk.unit_test()
