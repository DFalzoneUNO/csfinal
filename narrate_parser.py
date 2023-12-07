from tokens import Token, TokenType
from tokenizer import Tokenizer
from typing import List
from narrate_ast import *


class ParsingError(Exception):
    """This is what gets raised when the parser encounters something it shouldn't."""
    def __init__(self, message: str, line_number: int):
        super().__init__(f"Parsing error on line {line_number}: {message}")


class NarrateParser:
    def __init__(self, tokenizer: Tokenizer):
        self._tokenizer = tokenizer
        self._current_token: Token = self._tokenizer.get_next_token()

    @property
    def current_line(self) -> int:
        """This information passed to the constructor for `ParsingError`
        so that users can be told which line is erroneous.
        """
        return self._tokenizer.current_line

    @property
    def current_token(self) -> Token:
        """Allows the current token to be accessed in a read-only manner, because
        we don't want it to be modified anywhere but in `self.consume`.
        """
        return self._current_token

    def consume(self, expected_token_type: TokenType):
        """If the current token's type is `expected_token_type`, then move
        to the next token; otherwise, raise a `ParsingError`.
        """
        if self.current_token.token_type is expected_token_type:
            self._current_token = self._tokenizer.get_next_token()
        else:
            raise ParsingError(
                f"Expected a token of type {expected_token_type}, but got {self.current_token}.",
                self.current_line
            )

    def parse_file(self) -> FileContent:
        """Assuming that the tokenizer is initialized with the contents of a file,
        this method parses that file's contents into an abstract syntax tree.
        """
        scenes: List[Scene] = []
        modules: List[Module] = []
        while self.current_token.token_type is not TokenType.Eof:
            match self.current_token.token_type:
                case TokenType.Scene:
                    scenes.append(self.parse_scene())
                case TokenType.Module:
                    modules.append(self.parse_module())
                case _:
                    raise ParsingError(
                        f'Expected "@scene" or "@module", but got {self.current_token} instead.',
                        self.current_line
                    )
        return FileContent(modules, scenes)

    def parse_scene(self) -> Scene:
        """Parse a scene, i.e. a semicolon-separated sequence of directives preceded
        by `@scene <identifier>:` and ending with `@end-scene`.
        """
        self.consume(TokenType.Scene)
        scene_id = self.current_token
        self.consume(TokenType.Identifier)
        self.consume(TokenType.Colon)
        directives: List[Directive] = []
        while self.current_token.token_type is not TokenType.EndScene:
            directives.append(self.parse_directive())
        self.consume(TokenType.EndScene)
        return Scene(scene_id, directives)

    def parse_module(self) -> Module:
        """Parse a module, i.e. a sequence of scenes preceded by `@module <identifier>:`
        and ending with `@end-module <identifier>`.
        
        The reason why the module identifier must be repeated after `@end-module` is
        because a module may often be longer than the height of the programmer's screen,
        and I don't like the idea of seeing `@end-module` somewhere in one's code and
        having to scroll back up to find out exactly what module ends there.
        """
        self.consume(TokenType.Module)
        module_id = self.current_token
        self.consume(TokenType.Identifier)
        self.consume(TokenType.Colon)
        scene_list: List[Scene] = []
        while self.current_token.token_type is not TokenType.EndModule:
            scene_list.append(self.parse_scene())
        self.consume(TokenType.EndModule)
        closing_id = self.current_token
        self.consume(TokenType.Identifier)
        if module_id.value != closing_id.value:
            raise ParsingError(
                f'A module starting with "@module {module_id.value}:" must end with "@end-module {module_id.value}".',
                self.current_line
            )
        return Module(module_id, scene_list)

    def parse_directive(self) -> Directive:
        """Parse a directive, which is a statement inside a scene that specifies that scene's runtime
        behavior.
        """
        match self.current_token.token_type:
            case TokenType.Flavortext:
                return self.parse_flavortext_directive()
            case TokenType.Select:
                return self.parse_select_directive()
            case TokenType.Get:
                return self.parse_get_directive()
            case TokenType.Lose:
                return self.parse_lose_directive()
            case other:
                raise ParsingError(f'Expected directive "flavortext", "select", "get", or "lose", but got {other.value}.', self.current_line)

    def parse_flavortext_directive(self) -> FlavortextDirective:
        """Parse a flavortext directive, which specifies what a scene should print for the
        player to read.
        """
        self.consume(TokenType.Flavortext)
        self.consume(TokenType.OpenBrace)
        text = self.current_token
        self.consume(TokenType.String)
        self.consume(TokenType.CloseBrace)
        self.consume(TokenType.Semicolon)
        return FlavortextDirective(text)

    def parse_select_directive(self) -> SelectDirective:
        """Parse a select directive, which specifies the options available to the player
        to pick the next scene to move to.
        """
        self.consume(TokenType.Select)
        self.consume(TokenType.OpenBrace)
        options: List[SelectOption] = []
        while self.current_token.token_type is not TokenType.CloseBrace:
            options.append(self.parse_select_option())
            if self.current_token.token_type is TokenType.Comma:
                self.consume(TokenType.Comma)
            else:
                break
        self.consume(TokenType.CloseBrace)
        self.consume(TokenType.Semicolon)
        return SelectDirective(options)

    def parse_get_directive(self) -> GetDirective:
        """Parse a get directive, which adds an item to the player's inventory."""
        self.consume(TokenType.Get)
        item = self.current_token
        self.consume(TokenType.String)
        self.consume(TokenType.Semicolon)
        return GetDirective(item)

    def parse_lose_directive(self) -> LoseDirective:
        """Parse a lose directive, which removes an item from the player's inventory."""
        self.consume(TokenType.Lose)
        item = self.current_token
        self.consume(TokenType.String)
        self.consume(TokenType.Semicolon)
        return LoseDirective(item)

    def parse_select_option(self) -> SelectOption:
        """Parse a select option. A select directive contains a list of these.
        These comprise the things that the player can choose to do during a given scene.
        """
        condition: None | SelectCondition = None
        if self.current_token.token_type is TokenType.Has:
            condition = self.parse_select_condition()
        string_label = self.current_token.value
        self.consume(TokenType.String)
        self.consume(TokenType.Arrow)
        target = self.parse_select_target()
        return SelectOption(condition, string_label, target)

    def parse_select_condition(self) -> SelectCondition:
        """Parse the condition of a select option. This consists of a comma-separated
        list of predicates like `has "evil sword"` and `has no "ferry ticket"`; if any of
        those predicates are not true, then that option is not visible to the player.
        """
        included: List[Token] = []
        excluded: List[Token] = []
        while self.current_token.token_type is not TokenType.QuestionMark:
            self.consume(TokenType.Has)
            if self.current_token.token_type is TokenType.No:
                self.consume(TokenType.No)
                excluded.append(self.current_token)
            else:
                included.append(self.current_token)
            self.consume(TokenType.String)
            if self.current_token.token_type is not TokenType.QuestionMark:
                self.consume(TokenType.Comma)
        self.consume(TokenType.QuestionMark)
        return SelectCondition(included, excluded)

    def parse_select_target(self) -> SceneReference | FileReference:
        """Parse the target of a select option, i.e. a scene or file reference. The 'target' is
        where control flow goes if the associated option is selected.
        """
        if self.current_token.token_type is TokenType.Identifier:
            top_level_id = self.current_token
            self.consume(TokenType.Identifier)
            scene_id, module_id = None, None
            if self.current_token.token_type is TokenType.Scope:
                module_id = top_level_id
                self.consume(TokenType.Scope)
                scene_id = self.current_token
                self.consume(TokenType.Identifier)
            else:
                scene_id = top_level_id
            return SceneReference(module_id, scene_id)
        else:
            self.consume(TokenType.FileReference)
            self.consume(TokenType.OpenParen)
            filename = self.current_token.value
            self.consume(TokenType.String)
            self.consume(TokenType.CloseParen)
            self.consume(TokenType.Scope)
            scene_id, module_id = None, None
            top_level_id = self.current_token
            self.consume(TokenType.Identifier)
            if self.current_token.token_type is TokenType.Scope:
                # e.g. @file("foo.nar")::bar::baz
                module_id = top_level_id
                self.consume(TokenType.Scope)
                scene_id = self.current_token
                self.consume(TokenType.Identifier)
            else:
                # e.g. @file("foo.nar")::buzz
                scene_id = top_level_id
            return FileReference(filename, module_id, scene_id)
