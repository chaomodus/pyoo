import itertools

from .base import verb


class Thing(object):
    def __init__(self, thingname, description="A nondescript object."):
        names = [x.strip() for x in thingname.split(",")]
        self.name = names[0]
        self.names = tuple(names)
        self.description = description
        self.location = None
        self.interpreter = None

    def verbs(self):
        """Return a list of bound methods which denote themselves as verbs."""
        verbs = list()
        for item in dir(self):
            try:
                v = self.__getattribute__(item)
                if v.is_verb:
                    verbs.append(v)
            except AttributeError:
                continue
        return verbs

    def verb_globs(self):
        """Return a list of (globstr, bound method) where commands matching globstr should call method (given that
        'that' matches an object in the soup).
        """
        verbglobs = list()
        for vrb in self.verbs():
            vvars = [vrb.names]
            if vrb.callspec[0] == "this":
                vvars.append(self.names)
            elif vrb.callspec[0] in ("that", "any"):
                vvars.append(("*",))

            if vrb.callspec[1] != "none":
                vvars.append(vrb.callspec[1])

            if vrb.callspec[2] == "this":
                vvars.append(self.names)
            elif vrb.callspec[2] in ("that", "any"):
                vvars.append(("*",))

            for combo in itertools.product(*vvars):
                globstr = " ".join(combo)
                verbglobs.append((globstr, tuple(combo), vrb, self))
        return verbglobs

    def handle_move(self, newlocation):
        self.location = newlocation

    def __repr__(self):
        return "<Thing '%s' object at 0x%x>" % (self.name, self.__hash__())


class Container(Thing):
    def __init__(self, names, description=""):
        Thing.__init__(self, names, description)
        self.contents = list()

    def handle_enter(self, newobj):
        pass

    def __repr__(self):
        return "<Container '%s' object at 0x%x>" % (self.name, self.__hash__())


class Place(Container):
    def __init__(self, names, description=""):
        Container.__init__(self, names, description)
        self.ways = dict()

    # this verb expects to be annotated from update_go. We never want it ot be at the top of a match list by its deault
    # name either
    @verb("#go", "none", "none", "none")
    def go(self, verbname, dobjstr, prepstr, iobjstr, dobj, iobj, argstr):
        self.do_go(verbname)

    @verb("go,move,walk,run", "any", "none", "none")
    def go_dir(self, verbname, dobjstr, prepstr, iobjstr, dobj, iobj, argstr):
        self.do_go(dobjstr)

    def do_go(self, direction):
        if self.interpreter:
            if direction in self.ways:
                self.interpreter.handle_move(self.ways[direction])

    def update_go(self):
        # note does no actually remove items from the go verb in case the descender is overloading.
        # also note, the interpreter needs to have update() called after this is called.
        for direction in self.ways:
            if direction not in self.go.names:
                self.go.names.append(direction)

    def __repr__(self):
        return "<Place '%s' object at 0x%x>" % (self.name, self.__hash__())


class Player(Thing):
    def __init__(self):
        Thing.__init__(self, "player")
        self.inventory = list()

    def __repr__(self):
        return "<Player '%s' object at 0x%x>" % (self.name, self.__hash__())
