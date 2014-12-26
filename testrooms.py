import pyoo
from pyoo import PlaceLoader, Thing, verb, Interpreter, Container, Place, Player, PyooVerbNotFound

class DescriptivePlace(Place):
    def handle_enter(self, player):
        self.do_look()

    @verb('look,l', 'none','none','none')
    def look(self, verbname, dobjstr, prepstr, iobjstr, dobj, iobj, argstr):
        self.do_look()

    def do_look(self):
        print self.name
        if isinstance(self.description, basestring):
            print self.description
        else:
            for line in self.description:
                print line

loader = PlaceLoader(file('roomtest.txt','r'), DescriptivePlace)
game = Interpreter([], Player(), loader.places.values(), None)
porch = game.get_placematches('Porch')[0][1]
run = True

# REPL
if __name__ == '__main__':
    game.handle_move(porch)
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
