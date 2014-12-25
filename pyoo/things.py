import string
import functools
import itertools

from .base import verb

class Thing(object):
    def __init__(self, thingname, description="A nondescript object."):
        names = [x.strip() for x in thingname.split(',')]
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
        """Return a list of (globstr, bound method) where commands matching globstr should call method (given that 'that' matches an object in the soup)."""
        verbglobs = list()
        for verb in self.verbs():
            vvars = [verb.names,]
            if verb.callspec[0] == 'this':
                vvars.append(self.names)
            elif verb.callspec[0] in ('that','any'):
                vvars.append(('*',))

            if verb.callspec[1] != 'none':
                vvars.append(verb.callspec[1])

            if verb.callspec[2] == 'this':
                vvars.append(self.names)
            elif verb.callspec[2] in ('that','any'):
                vvars.append(('*',))

            for combo in itertools.product(*vvars):
                globstr = ' '.join(combo)
                verbglobs.append((globstr, tuple(combo), verb, self))
        return verbglobs

    def handle_move(self, newlocation):
        self.location = newlocation

    def __repr__(self):
        return "<Thing '%s' object at 0x%x>" % (self.name, self.__hash__())

class Container(Thing):
    def __init__(self, names, description=''):
        Thing.__init__(self, names, description)
        self.contents = list()

    def handle_enter(self, newobj):
        pass

    def __repr__(self):
        return "<Container '%s' object at 0x%x>" % (self.name, self.__hash__())

class Place(Container):
    def __init__(self, names, description=''):
        Container.__init__(self, names, description)
        self.ways = dict()

    # this verb expects to be annotated from update_go. We never want it ot be at the top of a match list by its deault name either
    @verb('#go','none','none','none')
    def go(self, verbname, dobjstr, prepstr, iobjstr, dobj, iobj, argstr):
        if self.interpreter:
            if self.ways.has_key(verbname):
                self.interpreter.handle_move(self.ways[verbname])

    def update_go(self):
        # note does no actually remove items from the go verb in case the descender is overloading.
        # also note, the interpreter needs to have update() called after this is called.
        for direction in ways:
            if not direction in self.go.names:
                self.go.names.append(direction)

    def __repr__(self):
        return "<Place '%s' object at 0x%x>" % (self.name, self.__hash__())


class Player(Thing):
    def __init__(self):
        Thing.__init__(self, 'player')
        self.inventory = list()

    def __repr__(self):
        return "<Player '%s' object at 0x%x>" % (self.name, self.__hash__())
