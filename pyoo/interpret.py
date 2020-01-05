import fnmatch

from .base import VerbCallFrame, PyooVerbNotFound, PyooObjectNotFound


class Interpreter(object):
    def __init__(self, contents = None):
        if contents is None:
            contents = []
        self.contents = set(contents)
        for cont in self.contents:
            cont.interpreter = self

        self.update()

    def add_player(self, player_object):
        self.contents.add(player_object)
        player_object.interpreter = self
        self.update()

    def remove_player(self, player_object):
        self.contents.remove(player_object)
        self.update()

    def update(self):
        self.update_caches()

    def update_caches(self):
        for obj in self.contents:
            try:
                obj.update_caches()
            except AttributeError:
                pass

    def handle_move(self, newroom, player):
        if player.location:
            player.location.handle_exit(player)
        newroom.handle_enter(player)

    def handle_get(self, thing):
        pass

    def lookup_object(self, player, objstr):
        m = None
        try:
            m = player.get_name_matches(objstr)
        except PyooObjectNotFound:
            m = None
        if not m and player.location:
            m = player.location.get_name_matches(objstr)
        if m:
            return m[0][1]
        else:
            return None


    def interpret(self, command, player):
        # FIXME make this better to support mulitple word objstrs and prepstr

        cmd_comps = command.split()
        verbstr = cmd_comps[0]
        dobjstr = ""
        prepstr = ""
        iobjstr = ""
        argstr = ""

        try:
            argstr = " ".join(cmd_comps[1:])
        except IndexError:
            pass

        try:
            dobjstr = cmd_comps[1]
            prepstr = cmd_comps[2]
            iobjstr = cmd_comps[3]
        except IndexError:
            pass
        try:
            cmdmatches = player.get_command_matches(command)
        except PyooVerbNotFound:
            if player.location:
                cmdmatches = player.location.get_command_matches(command)
            else:
                raise PyooVerbNotFound

        cmd = cmdmatches[0]
        # glob = cmd[0]
        # comps = cmd[1]
        verb = cmd[2]
        this = cmd[3]

        dobj = None
        if verb.callspec[0] == "this":
            dobj = this
        elif verb.callspec[0] == "that":
            # lookup object
            dobj = self.lookup_object(player, dobjstr)

        iobj = None
        if verb.callspec[2] == "this":
            iobj = this
        elif verb.callspec[2] == "that":
            # lookp object
            iobj = self.lookup_object(player, iobjstr)

        return verb(VerbCallFrame(self, verbstr, dobj, dobjstr, prepstr, iobj, iobjstr, argstr))
