from tokens import Token, TokenType
from tokenizer import Tokenizer
from typing import List
from narrate_ast import *


class ParsingError(Exception):
    def __init__(self, message: str, line_number: int):
        super().__init__(f"Parsing error on line {line_number}: {message}")


class NarrateParser:
    def __init__(self, tokenizer: Tokenizer):
        self._tokenizer = tokenizer
        self._current_token: Token = self._tokenizer.get_next_token()

    @property
    def current_line(self) -> int:
        return self._tokenizer.current_line

    @property
    def current_token(self) -> Token:
        return self._current_token

    def consume(self, expected_token_type: TokenType):
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
                case other:
                    raise ParsingError(f'Expected "@scene" or "@module", but got {other} instead.')
        return FileContent(modules, scenes)

    def parse_scene(self) -> Scene:
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
        self.consume(TokenType.Flavortext)
        self.consume(TokenType.OpenBrace)
        text = self.current_token
        self.consume(TokenType.String)
        self.consume(TokenType.CloseBrace)
        self.consume(TokenType.Semicolon)
        return FlavortextDirective(text)

    def parse_select_directive(self) -> SelectDirective:
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
        self.consume(TokenType.Get)
        item = self.current_token
        self.consume(TokenType.String)
        self.consume(TokenType.Semicolon)
        return GetDirective(item)

    def parse_lose_directive(self) -> LoseDirective:
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
