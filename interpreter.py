from typing import List
from narrate_ast import *
from narrate_parser import NarrateParser
from tokenizer import Tokenizer

class Interpreter:
    def __init__(
        self,
        src_filename: str,
        inventory: List[str] = [],
        next_scene_id: str = "start::main"
    ):
        self.set_interpreter_context(src_filename, inventory, next_scene_id)

    def set_interpreter_context(
        self,
        src_filename: str,
        inventory: List[str] = [],
        next_scene_id: str = "start::main"
    ):
        self.src_filename = src_filename
        with open(self.src_filename, "r") as src_file:
            self.src_code: str = src_file.read()
        tokenizer = Tokenizer(self.src_code)
        parser = NarrateParser(tokenizer)
        self.ast = parser.parse_file()
        self.inventory = inventory
        self.scene_id = next_scene_id

    def execute_scene(self, scene_id: str):
        scene = self.ast.get_scene(scene_id)
        for directive in scene.directives:
            # TODO
            pass

