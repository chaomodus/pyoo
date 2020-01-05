from pyoo.things import Place, Player
from pyoo.placeloader import PlaceLoader
from pyoo.interpret import Interpreter, PyooVerbNotFound
from pyoo.base import make_verb

class DescriptivePlace(Place):
    def handle_enter(self, player):
        super().handle_enter(player)
        self.do_look()

    @make_verb("look,l", "none", "none", "none")
    def look(self, verb_callframe):
        self.do_look()

    def do_look(self):
        print(self.name)
        if isinstance(self.description, str):
            print(self.description)
        else:
            for line in self.description:
                print(line)


loader = PlaceLoader(open("roomtest.txt", "r"), DescriptivePlace)
player = Player("player")
game = Interpreter(list(loader.places.values()))
porch = game.lookup_global_object("Porch")[0][1]
run = True
game.update()
game.handle_move(porch, player)

# REPL
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
