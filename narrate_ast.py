from abc import ABC
from typing import Literal
from tokens import TokenType, Token


class AstNode(ABC):
    pass


class Directive(AstNode):
    def __init__(self, directive_kw: Literal["flavortext", "get", "lose", "has", "select"]):
        self.directive_type = directive_kw


class SelectCondition(AstNode):
    pass


class FileReference(AstNode):
    def __init__(self, filename: str, module_id: Token | None, scene_id: Token):
        self.filename = filename
        if module_id is not None:
            if module_id.token_type is TokenType.Identifier:
                self.module_id: Token | None = module_id
            else:
                raise ValueError(f"Module ID should be TokenType.Identifier, got {module_id.token_type}")
        else:
            self.module_id: Token | None = None
        if scene_id.token_type is TokenType.Identifier:
            self.scene_id: Token = scene_id
        else:
            raise ValueError(f"Scene ID should be TokenType.Identifier, got {scene_id.token_type}")

    def __str__(self):
        if self.module_id is None:
            return f"(FileReference \"{self.filename}\"::{self.scene_id.value})"
        else:
            return f"(FileReference \"{self.filename}\"::{self.module_id.value}::{self.scene_id.value})"


class SelectOption(AstNode):
    def __init__(
        self,
        condition: None | SelectCondition,
        string_label: str,
        target: Token | FileReference
    ):
        self.condition = condition
        self.string_label = string_label
        if type(target) is Token:
            if target.token_type is not TokenType.Identifier:
                raise ValueError(
                    f"Target of select option should be TokenType.Identifier, got {target.token_type}"
                )
            else:
                self.target: Token | FileReference = target
        else:
            self.target: Token | FileReference = target

    def __str__(self):
        if self.condition is None:
            return f"(SelectOption \"{self.string_label}\" => {self.target})"
        else:
            return f"(SelectOption {self.condition} ? \"{self.string_label}\" => {self.target})"
