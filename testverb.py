import pyoo
from pyoo import Thing, verb, Pyoo, Container, Place, Player, PyooVerbNotFound

class Hammer(Thing):
    def __init__(self):
        Thing.__init__(self, 'hammer','a heavy ball-peen hammer.')

    @verb('hit','that','with','this')
    def hit(self, verbname, dobjstr, prepstr, iobjstr, dobj, iobj, argstr):
        try:
            dobj.handle_hit(self)
        except:
            pass

    @verb('drop','this','none','none')
    def drop(self, verbname, dobjstr, prepstr, iobjstr, dobj, iobj, argstr):
        print verbname, dobjstr, prepstr, iobjstr, dobj, iobj

    @verb('get','this','none','none')
    def get(self, verbname, dobjstr, prepstr, iobjstr, dobj, iobj, argstr):
        print verbname, dobjstr, prepstr, iobjstr, dobj, iobj

class Nail(Thing):
    def __init__(self):
        Thing.__init__(self, 'nail','a nine inch nail.')
        self.depth = 1

    def handle_hit(self, hitter):
        if self.depth > 0:
            print "bang! the nail is hammered."
            self.depth -= 1
        else:
            print "ping! the nail won't go deeper."

class HammerTime(Place):
    def __init__(self):
        Place.__init__(self, "HAMMERTIME")
        self.contents.append(Hammer())
        self.contents.append(Nail())

    @verb('look,l','none','none','none')
    def look(self, verbname, dobjstr, prepstr, iobjstr, dobj, iobj, argstr):
        if self.contents[1].depth > 0:
            print "You see a nail sticking out ", self.contents[1].depth, "cm."
        else:
            print "You see a nail fully hammered in."
        print "You see a hammer."

    @verb('look,l', 'that','none','none')
    def look_at(self, verbname, dobjstr, prepstr, iobjstr, dobj, iobj, argstr, stateobject=None):
        if dobj:
            print "%s: %s" % (dobj.name, dobj.description)
        else:
            print "That doesn't appear to be here."

hammertime = HammerTime()
game = Pyoo([], Player(), [hammertime,], hammertime)
run = True

if __name__ == '__main__':
    while (run):
        cmd = ''
        try:
            cmd = raw_input('>')
        except EOFError:
            run = False
        if cmd.startswith('quit'):
            run  = False
        else:
            try:
                game.interpret(cmd)
            except PyooVerbNotFound:
                print "I don't understand that."

    print "Bye!"
