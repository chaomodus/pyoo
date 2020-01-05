import fnmatch
import itertools

from .base import make_verb, PyooVerbNotFound, PyooObjectNotFound

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

    def handle_remove(self, oldlocation):
        self.location = None

    def __repr__(self):
        return "<Thing '%s' object at 0x%x>" % (self.name, self.__hash__())

class Container(Thing):
    def __init__(self, names, description=""):
        super().__init__(names, description)
        self.contents = set()
        self.name_cache = []
        self.command_cache = []

    def update_caches(self):
        self.name_cache = []
        self.command_cache = []
        for obj in self.contents:
            for name in obj.names:
                self.name_cache.append((name, obj))
            for verbglob in obj.verb_globs():
                if verbglob[0][0] == "#":
                    continue
                self.command_cache.append(verbglob)
        for verbglob in self.verb_globs():
            if verbglob[0][0] == "#":
                    continue
            self.command_cache.append(verbglob)

    def get_command_matches(self, command_spec):
        res = [x for x in self.command_cache if fnmatch.fnmatch(command_spec, x[0])]
        # sort by ambiguity (percentage of *)
        res.sort(key=lambda a: a[0].count("*") / float(len(a[0])))
        if (len(res) < 1):
            raise PyooVerbNotFound
        return res

    def get_name_matches(self, name):
        return [x for x in self.name_cache if fnmatch.fnmatch(name, x[0])]

    def handle_exit(self, oldobj):
        self.contents.remove(oldobj)
        oldobj.handle_remove(self)

    def handle_enter(self, newobj):
        self.contents.add(newobj)
        newobj.handle_move(self)
        try:
            newobj.update_caches()
        except AttributeError:
            pass
        self.update_caches()

    def __repr__(self):
        return "<Container '%s' object at 0x%x>" % (self.name, self.__hash__())


class Place(Container):
    def __init__(self, names, description=""):
        super().__init__(names, description)
        self.ways = dict()

    # this verb expects to be annotated from update_go. We never want it ot be at the top of a match list by its deault
    # name either
    @make_verb("#go", "none", "none", "none")
    def go(self, verb_callframe):
        self.do_go(verb_callframe.verbname, verb_callframe)

    @make_verb("go,move,walk,run", "any", "none", "none")
    def go_dir(self, verb_callframe):
        self.do_go(verb_callframe.dobjstr, verb_callframe)

    def do_go(self, direction, verb_callframe):
        if direction in self.ways:
            verb_callframe.environment.handle_move(self.ways[direction],  verb_callframe.player)

    def update_go(self):
        # note does no actually remove items from the go verb in case the descender is overloading.
        # also note, the interpreter needs to have update() called after this is called.
        for direction in self.ways:
            if direction not in self.go.names:
                self.go.names.append(direction)
        if self.interpreter:
            self.interpreter.update()

    def __repr__(self):
        return "<Place '%s' object at 0x%x>" % (self.name, self.__hash__())


class Player(Container):
    def __init__(self, names, description=""):
        super().__init__(names, description)

    def __repr__(self):
        return "<Player '%s' object at 0x%x>" % (self.name, self.__hash__())
