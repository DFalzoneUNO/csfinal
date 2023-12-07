from abc import ABC
from typing import Literal, List
from tokens import TokenType, Token


class AstNode(ABC):
    """Abstract base class for nodes of a Narrate abstract syntax tree."""
    def __str__(self):
        raise NotImplementedError(
            "Internal error: AstNode.__str__ is an abstract method; child classes must override it."
        )


class Directive(AstNode):
    """Base class for directives, which are different from other AST nodes because
    directives specify the interpreter's runtime behavior rather than the static
    structure of the code.
    """
    def __init__(self, directive_kw: Literal["flavortext", "get", "lose", "has", "select"]):
        self.directive_type: Literal["flavortext", "get", "lose", "has", "select"] = directive_kw


class SelectCondition(Directive):
    """Represents the optional `has` directive that may precede a select
    option to make that option conditionally visible, e.g.
    `has "Sword", no "Shield" ? "Fight with no shield" => get-stabbed,`
    """
    def __init__(self, included: List[Token], excluded: List[Token]):
        """Constructor for `SelectCondition`.
        :param included: list of items that must be in the player's inventory for the condition to be true
        :param excluded: list of items that cannot be in the player's inventory for the condition to be true
        """
        super().__init__("has")
        if any(token.token_type is not TokenType.String for token in [*included, *excluded]):
            raise ValueError("Parameters to `has` directive must all be strings!")
        self.included: List[Token] = included
        self.excluded: List[Token] = excluded

    def __str__(self):
        has = " ".join(f'"{item.value}"' for item in self.included)
        has_not = " ".join(f'"{item.value}"' for item in self.excluded)
        return f'(SelectCondition (has ({has})) (has no ({has_not})))'


class FileReference(AstNode):
    """Represents a reference to a scene defined in another file, which can be used as
    the target of a select option. E.g. `@file("./foo.nar")::bar::baz` refers to scene
    `baz` defined in module `bar` defined in the file `./foo.nar`.
    """
    def __init__(self, filename: str, module_id: Token | None, scene_id: Token):
        self.filename = filename
        if module_id is not None:
            if module_id.token_type is TokenType.Identifier:
                self.module_id: Token | None = module_id
            else:
                raise ValueError(f"Module ID should be TokenType.Identifier, got {module_id.token_type}.")
        else:
            self.module_id: Token | None = None
        if scene_id.token_type is TokenType.Identifier:
            self.scene_id: Token = scene_id
        else:
            raise ValueError(f"Scene ID should be TokenType.Identifier, got {scene_id.token_type}.")

    @property
    def scoped_scene_id(self) -> str:
        """A module ID is the identifier that refers to a module, not including a specific scene.

        A scene ID is the identifier of a scene, with or without the specific module ID preceding it.

        A scoped scene ID is specifically a module ID *with* the ID of a scene contained within that
        module. That's what this property returns: the scoped scene ID attached to a file reference.
        """
        if self.module_id is not None:
            return f"{self.module_id.value}::{self.scene_id.value}"
        else:
            return self.scene_id.value

    def __str__(self):
        if self.module_id is None:
            return f"(FileReference \"{self.filename}\"::{self.scene_id.value})"
        else:
            return f"(FileReference \"{self.filename}\"::{self.module_id.value}::{self.scene_id.value})"


class SceneReference(AstNode):
    """Represents a scene ID which can be used as a select option target referring to a scene
    defined in the same file.
    """
    def __init__(self, module_id: Token | None, scene_id: Token):
        if module_id is not None and module_id.token_type is not TokenType.Identifier:
            raise ValueError(f"Module ID should be TokenType.Identifier, got {module_id.token_type}.")
        elif scene_id.token_type is not TokenType.Identifier:
            raise ValueError(f"Scene ID should be TokenType.Identifier, got {scene_id.token_type}.")
        self.module_id = module_id
        self.scene_id = scene_id
    
    def __str__(self):
        """For convenience, this class's `__str__` method returns the scoped scene identifier as
        it would appear in Narrate source code.
        """
        if self.module_id is None:
            return f"{self.scene_id.value}"
        else:
            return f"{self.module_id.value}::{self.scene_id.value}"


class SelectOption(AstNode):
    """Represents one of the options that may be presented to the player when a scene is executed.
    E.g. `has "shield" ? "Try to Fight" => fighting-time`
    """
    def __init__(self, condition: None | SelectCondition, string_label: str, target: SceneReference | FileReference):
        self.condition = condition
        self.string_label = string_label
        self.target = target

    def __str__(self):
        if self.condition is None:
            return f"(SelectOption \"{self.string_label}\" => {self.target})"
        else:
            return f"(SelectOption {self.condition} ? \"{self.string_label}\" => {self.target})"


class FlavortextDirective(Directive):
    """A flavortext directive displays text to the player providing context
    and immersion during the execution of a scene.
    """
    def __init__(self, text: Token):
        super().__init__("flavortext")
        if text.token_type is not TokenType.String:
            raise ValueError(
                f"Flavortext content should be a string, got {text.token_type}."
            )
        self.text = text

    def __str__(self):
        return f"(FlavortextDirective {self.text})"


class SelectDirective(Directive):
    """A select directive contains a list of options which may be presented to the player to prompt
    for which scene to go to next.
    """
    def __init__(self, options: List[SelectOption]):
        super().__init__("select")
        self.options = options

    def __str__(self):
        options = "\n\t".join(str(option) for option in self.options)
        return f"(SelectDirective (\n\t{options}))"


class InventoryDirective(Directive):
    """A `get` or `lose` directive modifies the contents of the player's inventory."""
    def __init__(self, directive_kw: Literal["get", "lose"], item: Token):
        super().__init__(directive_kw)
        if item.token_type is not TokenType.String:
            raise ValueError(f"{self.directive_type} directive expects a string literal, got {str(item)} instead.")
        self.item = item

    def __str__(self):
        return f"({self.directive_type} {self.item})"


class GetDirective(InventoryDirective):
    """Adds an item to the player's inventory."""
    def __init__(self, item: Token):
        super().__init__("get", item)


class LoseDirective(InventoryDirective):
    """Removes an item from the player's inventory."""
    def __init__(self, item: Token):
        super().__init__("lose", item)


class Scene(AstNode):
    """An adventure is organized into scenes, specific points in the story where the player is given
    story text to read and options to decide where to take the story next.
    """
    def __init__(self, identifier: Token, directives: List[Directive]):
        if identifier.token_type is not TokenType.Identifier:
            raise ValueError(f"Scene should have an identifier, but instead there is a {identifier.token_type}.")
        self.identifier = identifier

        # Every scene must have one select directive.
        select_directives = [d for d in directives if type(d) is SelectDirective]
        if len(select_directives) == 0:
            raise ValueError(f"A scene has to have a select directive in it, but scene {self.identifier.value} does not.")
        elif len(select_directives) > 1:
            raise ValueError(f"A scene must have only one select directive, but scene {self.identifier.value} has {len(select_directives)}.")

        self.directives = directives

    def __str__(self):
        directives_str = "\n\t".join([str(d) for d in self.directives])
        return f"(Scene (\n\t{directives_str}))"


class Module(AstNode):
    """Scenes can be organized into modules so that many related scenes can be conceptually grouped
    together in the programmer's mind, and so that scene identifiers don't pollute the global namespace.
    """
    def __init__(self, module_id: Token, scenes: List[Scene]):
        if module_id.token_type is not TokenType.Identifier:
            raise ValueError(f"Expected module identifier to be TokenType.Identifier but got {module_id.token_type} instead.")
        self.module_id = module_id
        self.scene_list = scenes
    
    def __str__(self):
        scene_list_str = "\n".join([str(scene) for scene in self.scene_list])
        return f"(Module (id {self.module_id.value}) (\n{scene_list_str}))"


class FileContent(AstNode):
    """Represents the root of the AST, which contains all the scenes and modules in a file. A higher
    level of organization than this is not necessary for the interpreter, since the filesystem itself
    is already an effective way to organize files.
    """
    def __init__(self, modules: List[Module], scenes: List[Scene]):
        if len(modules) == 0 and len(scenes) == 0:
            raise ValueError(f"A file must contain at least one module or scene.")
        self.module_list = modules
        self.scene_list = scenes
    
    def get_scene(self, identifier: str) -> Scene:
        """This takes a scene identifier and returns the corresponding scene from that file if that
        scene exists. If a scene is inside a module, the scope operator :: is used, e.g. foo::bar
        refers to the scene bar defined in the module foo.
        """
        if "::" in identifier:
            module_id, scene_id = identifier.split("::")
            for module in self.module_list:
                if module.module_id.value == module_id:
                    for scene in module.scene_list:
                        if scene.identifier.value == scene_id:
                            return scene
            raise ValueError(f"Tried to find a scene named {scene_id} in a module named {module_id}, but couldn't.")
        else:
            scene_id = identifier
            for scene in self.scene_list:
                if scene.identifier.value == identifier:
                    return scene
            raise ValueError(f"Tried to find a scene named {scene_id}, but couldn't.")
    
    def __str__(self):
        modules = "\n\t".join([str(module) for module in self.module_list])
        scenes = "\n\t".join([str(scene) for scene in self.scene_list])
        return f"(FileContent\n(modules {modules})\n(scenes {scenes}))"
