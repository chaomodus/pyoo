
from .things import Place

(ST_START, ST_DESC, ST_EXITS) = range(3)

class PlaceLoader(object):
    def __init__(self, infile, baseplace=Place):
        """Create the factory by reading the contents of infile (an iteratable object [file-like or otherwise]). Specify the base class for place with baseplace."""
        self.base = baseplace
        self.places = dict() #indexed by name

        if infile:
            self.process_file(infile)

    def process_file(self, inf):
        state = ST_START
        rm = None
        desc = list()
        for line in inf:
            line = line.strip()
            if state == ST_START:
                rm = self.base(line)
                rm.temp_exits = list()
                state = ST_DESC
                desc = list()
            elif state == ST_DESC:
                if line == '.':
                    state = ST_EXITS
                    rm.description = desc
                else:
                    desc.append(line)
            elif state == ST_EXITS:
                if line == '.':
                    state = ST_START
                    self.places[rm.name] = rm
                    rm = None
                else:
                    rm.temp_exits.append(line)

        # assemble the exits
        for place in self.places.values():
            for ext in place.temp_exits:
                names, destination = ext.split(' ',1)
                for nm in names.split(','):
                    place.ways[nm] = self.places[destination]
                place.update_go()
