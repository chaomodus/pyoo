from pyoo.interpret import Interpreter
from pyoo.things import Thing, Place, Player
from pyoo.base import make_verb, PyooVerbNotFound

class Hammer(Thing):
    def __init__(self):
        Thing.__init__(self, "hammer", "a heavy ball-peen hammer.")

    @make_verb("hit", "that", "with", "this")
    def hit(self, verb_callframe):
        try:
            verb_callframe.dobj.handle_hit(self)
        except AttributeError:
            pass

    @make_verb("drop", "this", "none", "none")
    def drop(self, verb_callframe):
        print(verb_callframe)

    @make_verb("get", "this", "none", "none")
    def get(self, verb_callframe):
        print(verb_callframe)


class Nail(Thing):
    def __init__(self):
        Thing.__init__(self, "nail", "a nine inch nail.")
        self.depth = 1

    def handle_hit(self, hitter):
        if self.depth > 0:
            print("bang! the nail is hammered.")
            self.depth -= 1
        else:
            print("ping! the nail won't go deeper.")

    def contents_desc_hook(self):
        if self.depth > 0:
            return "You see a nail sticking out "+str(self.depth)+"cm."
        else:
            return "You see a nail fully hammered in."

class HammerTime(Place):
    def __init__(self):
        Place.__init__(self, "HAMMERTIME")
        self.handle_enter(Hammer())
        self.handle_enter(Nail())


    @make_verb("look,l", "none", "none", "none")
    def look(self, verb_callframe):
        for cont in self.contents:
            try:
                print(cont.contents_desc_hook())
            except AttributeError:
                continue
        print("You see a hammer.")

    @make_verb("look,l", "that", "none", "none")
    def look_at(self, verb_callframe):
        if verb_callframe.dobj:
            dobj = verb_callframe.dobj
            print("%s: %s" % (dobj.name, dobj.description))
        else:
            print("That doesn't appear to be here.")


hammertime = HammerTime()
game = Interpreter([hammertime])
player = Player("player")
game.add_player(player)
game.handle_move(hammertime, player)
game.update()
run = True
if __name__ == "__main__":
    while run:
        cmd = ""
        try:
            cmd = input(">")
        except EOFError:
            run = False
        if cmd.startswith("quit"):
            run = False
        else:
            try:
                game.interpret(cmd, player)
            except PyooVerbNotFound:
                print("I don't understand that.")

    print("Bye!")
