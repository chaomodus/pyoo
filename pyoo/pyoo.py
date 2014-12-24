import string
import functools
import itertools
import fnmatch

prepositions = ('with/using',
                'at/to',
                # 'in front of',
                'in/inside/into',
                # 'on top of/on/onto/upon',
                # 'out of/from inside/from',
                'over',
                'through',
                'under/underneath/beneath',
                'behind',
                'beside',
                'for/about',
                'is',
                'as',
                'off')
                #'off/off of')

normalized_preps = tuple([x.split('/') for x in prepositions])

class PyooError(Exception):
    pass

class PyooVerbNotFound(PyooError):
    pass

# this simple decorator adds verb metadata to a method or function
# verbname is a comma-separated list of verb names with possible woldcard
# dobjspec is 'this' or 'that' or 'none' or 'any' (this = the object which defines the verb, that = an object in the soup, any = any string, none = blank)
# iobjspec is 'this' or 'that' or 'none' or 'any'
# prepspec is one of prepositions strings
# verb prototypes are: (verbname, dobjstr, prepstr, iobjstr, dobj, iobj, argstr)
def verb(verbname, dobjspec, prepspec, iobjspec):
    def verb_decorate(verbfunc):
        names = [x.strip() for x in verbname.split(',')]
        verbfunc.name = names[0]
        verbfunc.names = tuple(names)
        ps = prepspec
        if isinstance(ps, basestring):
            if ps.find('/') > 0:
                ps = ps.split('/')
            else:
                for p in normalized_preps:
                    if ps in p:
                        ps = p
                        break
        verbfunc.callspec = (dobjspec, ps, iobjspec)
        verbfunc.is_verb = True
        return verbfunc
    return verb_decorate

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

    def __repr__(self):
        return "<Container '%s' object at 0x%x>" % (self.name, self.__hash__())

class Place(Container):
    def __init__(self, names, description=''):
        Container.__init__(self, names, description)
        self.ways = dict()

    @verb('n,w,s,e,nw,sw,ne,se,u,d,in,out','none','none','none')
    def go(self, verbname, dobjstr, prepstr, iobjstr, dobj, iobj, argstr):
        if self.interpreter:
            if self.ways.has_key(verbname):
                self.interpreter.handle_move(self.ways[verbname])

    def __repr__(self):
        return "<Place '%s' object at 0x%x>" % (self.name, self.__hash__())


class Player(Thing):
    def __init__(self):
        Thing.__init__(self, 'player')
        self.inventory = list()

    def __repr__(self):
        return "<Player '%s' object at 0x%x>" % (self.name, self.__hash__())

class Pyoo(object):
    def __init__(self, defaultcontents=[], player=None, rooms=[], room=None):
        # the "working" contents
        self.contents = list()

        # name lookup caches
        self.namecache = list()
        self.commandcache = list()

        # the "player" object
        self.player = player
        if self.player:
            player.interpreter = self

        # the rooms that the player can move to
        self.rooms = rooms
        for rm in rooms:
            rm.interpreter = self
        self.room = room

        # the items and objets that are always with the player
        self.defaultcontents = defaultcontents
        for cont in self.defaultcontents:
            cont.interpreter = self

        self.update()

    def update(self):
        self.contents = list(self.defaultcontents)
        if self.room:
            self.contents.append(self.room)
            try:
                self.contents.extend(self.room.contents)
            except:
                pass
        if self.player:
            self.contents.append(self.player)
            try:
                self.contents.extend(self.player.inventory)
            except:
                pass

        self.update_namecache()
        self.update_commandcache()

    def update_namecache(self):
        self.namecache = list()
        for obj in self.contents:
            for name in obj.names:
                self.namecache.append((name, obj))

    def update_commandcache(self):
        self.commandcache = list()
        for obj in self.contents:
            for verbglob in obj.verb_globs():
                self.commandcache.append(verbglob)

    def get_matches(self, command):
        res =  [x for x in self.commandcache if fnmatch.fnmatch(command, x[0])]
        # sort by ambiguity (percentage of *)
        res.sort(lambda a,b: cmp(a[0].count('*') / float(len(a[0])), b[0].count('*') / float(len(b[0]))))
        return res

    def get_namematches(self, name):
        return [x for x in self.namecache if fnmatch.fnmatch(name, x[0])]

    def handle_move(self, newroom):
        self.room = newroom
        if self.player:
            try:
                self.player.handle_move(newroom)
            except: pass

    def handle_get(self, thing):
        pass

    def interpret(self, command):
        cmdmatches = self.get_matches(command)
        if not cmdmatches:
            raise PyooVerbNotFound()
        cmd = cmdmatches[0]
        glob  = cmd[0]
        comps = cmd[1]
        verb = cmd[2]
        this = cmd[3]

        # FIXME make this better to supprot mulitple word objstrs and prepstr

        cmd_comps = command.split(' ')
        verbstr = cmd_comps[0]
        dobjstr = ''
        prepstr = ''
        iobjstr = ''
        argstr = ''

        try:
            argstr = ' '.join(cmd_comps[1:])
        except IndexError:
            pass

        try:
            dobjstr = cmd_comps[1]
            prepstr = cmd_comps[2]
            iobjstr = cmd_comps[3]
        except IndexError:
            pass

        dobj = None
        if verb.callspec[0] == 'this':
            dobj = this
        elif verb.callspec[0] == 'that':
            # lookup object
            m = self.get_namematches(dobjstr)
            if m:
                dobj = m[0][1]
            else:
                # this is probably an error
                dobj = None

        iobj = None
        if verb.callspec[2] == 'this':
            iobj = this
        elif verb.callspec[2] == 'that':
            # lookp object
            m = self.get_namematches(iobjstr)
            if m:
                iobj = m[0][1]
            else:
                # this is probably an error
                iobj = None

        return verb(verbstr, dobjstr, prepstr, iobjstr, dobj, iobj, argstr)
