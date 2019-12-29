from enum import Enum
from typing import TextIO

from .things import Place, Thing


class PlaceLoaderStates(Enum):
    START = 0
    DESC = 1
    EXITS = 2


class PlaceLoader(object):
    """
    A factory which loads a simple data format containing a description of rooms, and how
    they are connected, and produces room objects for each one.
    """
    def __init__(self, in_file: TextIO, baseplace: Thing = Place):
        """Initialize the factory by loading a description file."""
        self.base = baseplace
        self.places = {}  # indexed by name

        if in_file:
            self.process_file(in_file)

    def process_file(self, in_file: TextIO):
        """Load any room information from the passed in file."""
        state = PlaceLoaderStates.START
        rm = None
        desc = []
        for line in in_file:
            line = line.strip()
            if state == PlaceLoaderStates.START:
                rm = self.base(line)
                rm.temp_exits = list()
                state = PlaceLoaderStates.DESC
                desc = list()
            elif state == PlaceLoaderStates.DESC:
                if line == ".":
                    state = PlaceLoaderStates.EXITS
                    rm.description = desc
                else:
                    desc.append(line)
            elif state == PlaceLoaderStates.EXITS:
                if line == ".":
                    state = PlaceLoaderStates.START
                    self.places[rm.name] = rm
                    rm = None
                else:
                    rm.temp_exits.append(line)

        # assemble the exits
        for place in list(self.places.values()):
            for ext in place.temp_exits:
                names, destination = ext.split(" ", 1)
                for nm in names.split(","):
                    place.ways[nm] = self.places[destination]
                place.update_go()
