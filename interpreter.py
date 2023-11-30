import sys
from typing import List, cast
from narrate_ast import *
from narrate_parser import NarrateParser
from tokenizer import Tokenizer

class Interpreter:
    def __init__(
        self,
        src_filename: str,
        entry_point_scene_id: str = "main"
    ):
        self.inventory: List[str] = []
        self.set_interpreter_context(src_filename, entry_point_scene_id)

    @property
    def inventory_lower(self) -> List[str]:
        """This property makes case-insensitive inventory management more convenient."""
        return [string.lower() for string in self.inventory]

    def set_interpreter_context(
        self,
        src_filename: str,
        scene_id: str
    ):
        self.src_filename = src_filename
        with open(self.src_filename, "r") as src_file:
            self.src_code: str = src_file.read()
        tokenizer = Tokenizer(self.src_code)
        parser = NarrateParser(tokenizer)
        self.ast = parser.parse_file()
        self.scene_id = scene_id

    def main_loop(self):
        """Run the interpreter indefinitely. Since every scene must include a `select`
        directive, we can expect calls to `self.execute_scene` to change the value of
        `self.scene_id` per the player's choices. See the other docstrings in this class's
        methods for info about how the interpreter knows when to halt execution.
        """
        while True:
            self.execute_scene(self.scene_id)

    def execute_scene(self, scene_id: str):
        """Loads a scene from the current file based on its scoped scene id and executes it.
        If the user selects an option with a target of `exit`, then this method terminates
        the program with `sys.exit`.
        """
        scene = self.ast.get_scene(scene_id)
        select_directive = None
        for d in scene.directives:
            match d.directive_type:
                case "get":
                    get_directive = cast(GetDirective, d)
                    self.inventory.append(get_directive.item.value)
                case "lose":
                    lose_directive = cast(LoseDirective, d)
                    # The method list.remove removes only the first instance of the value; that's just what we want.
                    if lose_directive.item.value.lower() in self.inventory_lower:
                        self.inventory.remove(lose_directive.item.value)
                case "flavortext":
                    flavortext_directive = cast(FlavortextDirective, d)
                    print(flavortext_directive.text.value)
                case "select":
                    select_directive = cast(SelectDirective, d)
        assert select_directive is not None
        game_over: bool = self.execute_select_directive(select_directive)
        if game_over:
            print(f"Game over. Your inventory contents:")
            for item in self.inventory:
                print(f"* {item}")
            sys.exit(0)

    
    def execute_select_directive(self, sd: SelectDirective) -> bool:
        """Print a list of options and let the user select one. If the target the user selects
        is a reference to another file, this method will set the interpreter's context to that file.
        Otherwise, if the target scene id is not `exit`, this method will set `self.scene_id` to the
        targeted scene id.

        If the target id is `exit`, this method returns `True`, else it returns `False`.
        
        `exit` is a reserved scene identifier which ends the current adventure, e.g.
        `"Jump into the razor blade tornado" => exit`
        """
        print("Options:")
        visible_options: List[SelectOption] = []
        for option in sd.options:
            if self.evaluate_has_directive(option.condition):
                visible_options.append(option)
        for i in range(len(visible_options)):
            print(f"[{i+1}] {visible_options[i].string_label}")
        selection_input = int(input('> ')) - 1 # TODO exception handling
        selection = visible_options[selection_input]
        if type(selection.target) is SceneReference:
            if str(selection.target) == "exit":
                return True
            else:
                self.scene_id = str(selection.target)
                return False
        else:
            assert type(selection.target) is FileReference
            target_id = selection.target.scoped_scene_id
            self.set_interpreter_context(selection.target.filename, target_id)
            return False

    def evaluate_has_directive(self, hd: SelectCondition | None) -> bool:
        if hd is None:
            return True
        inv = self.inventory_lower
        included: List[str] = [item.value.lower() for item in hd.included]
        excluded: List[str] = [item.value.lower() for item in hd.excluded]
        return all([item in inv for item in included]) and all([item not in inv for item in excluded])
