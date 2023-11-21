from abc import ABC
from typing import Literal, List
from tokens import TokenType, Token


class AstNode(ABC):
    pass


class Directive(AstNode):
    def __init__(self, directive_kw: Literal["flavortext", "get", "lose", "has", "select"]):
        self.directive_type = directive_kw


class SelectCondition(AstNode):
    """Class representing the optional `has` directive that may precede a select
    option to make that option conditionally visible, e.g.
    `has "Sword", no "Shield" ? "Fight with no shield" => get-stabbed,`
    """
    def __init__(self, included: List[Token], excluded: List[Token]):
        """Constructor for `SelectCondition`.
        :param included: list of items that must be in the player's inventory for the condition to be true
        :param excluded: list of items that cannot be in the player's inventory for the condition to be true
        """
        if any(token.token_type is not TokenType.String for token in [*included, *excluded]):
            raise ValueError("Parameters to `has` directive must all be strings!")
        self.included: List[Token] = included
        self.excluded: List[Token] = excluded

    def __str__(self):
        has = " ".join(f'"{item.value}"' for item in self.included)
        has_not = " ".join(f'"{item.value}"' for item in self.excluded)
        return f'(SelectCondition has ({has}) has no ({has_not}))'


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


class SelectDirective(Directive):
    def __init__(self, options: List[SelectOption]):
        super().__init__("select")
        self.options = options

    def __str__(self):
        options = "".join(f"\t{option}\n" for option in self.options)
        return f"(SelectDirective (\n{options}))"


class FlavortextDirective(Directive):
    def __init__(self, text: Token):
        super().__init__("flavortext")
        if text.token_type is not TokenType.String:
            raise ValueError(f"Flavortext content should be a string, got {text.token_type}")
        self.text = text

    def __str__(self):
        return f"(FlavortextDirective {self.text})"

# TODO: other directives; scenes; modules
