import string
import functools
import itertools
import fnmatch

from .base import prepositions, normalized_preps

class PyooError(Exception):
    pass

class PyooVerbNotFound(PyooError):
    pass

class Interpreter(object):
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
                # special case for internal verbs to opt out of matching by their default name, they start with #
                if verbglob[0][0] == '#':
                    continue
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

        try:
            self.room.handle_enter(player)
        except:
            pass


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
