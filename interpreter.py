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

    def execute_scene(self, scene_id: str):
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
                    print(flavortext_directive.text)
                case "select":
                    select_directive = cast(SelectDirective, d)
        assert select_directive is not None
        self.execute_select_directive(select_directive)

    
    def execute_select_directive(self, sd: SelectDirective):
        # TODO
        pass
