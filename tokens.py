from enum import StrEnum, auto


# https://stackoverflow.com/a/51226342/10942736
class TokenType(StrEnum):
    Module = "@module",
    Scene = "@scene",
    EndModule = "@end-module",
    EndScene = "@end-scene",
    FileReference = "@file"

    Flavortext = "flavortext",
    Select = "select",
    Has = "has",
    Get = "get",
    Lose = "lose",
    No = "no",

    Colon = ":",
    Semicolon = ";",
    OpenBrace = "{",
    CloseBrace = "}",
    Comma = ",",
    OpenParen = "(",
    CloseParen = ")",
    Condition = "?",
    Arrow = "=>",
    Scope = "::",

    String = auto(),
    Identifier = auto(),

    Eof = auto()


class Token:
    Keywords = [
        TokenType.Module, TokenType.EndModule,
        TokenType.Scene, TokenType.EndScene,
        TokenType.FileReference,
        TokenType.Flavortext,
        TokenType.Select,
        TokenType.Has,
        TokenType.No,
        TokenType.Get,
        TokenType.Lose
    ]

    Punctuation = [
        TokenType.Colon, TokenType.Semicolon, TokenType.Comma,
        TokenType.OpenBrace, TokenType.CloseBrace,
        TokenType.OpenParen, TokenType.CloseParen,
        TokenType.Condition, TokenType.Arrow,
        TokenType.Scope
    ]

    def __init__(self, token_type: TokenType, value: str | None = None):
        """Constructor parameters:
        :param token_type: the type of token as defined in the `TokenType` enum.
        :param value: if the token is a string literal or identifier, this is its value.
        """
        self.token_type = token_type
        if token_type in (TokenType.String, TokenType.Identifier):
            if value is None:
                raise ValueError("Token type expects string value but none was given")
            else:
                self.value = value
        else:
            self.value = token_type.value

    def __str__(self):
        """Human-readable string representation, strictly for debugging purposes."""
        if self.token_type in Token.Keywords:
            return f"(Keyword {self.value})"
        elif self.token_type in Token.Punctuation:
            return f"(Punctuation '{self.value}')"
        elif self.token_type is TokenType.Eof:
            return "(End of file)"
        else:
            escaped_value = self.value.replace('\n', '\\n').replace('"', '\\"')
            return f'({self.token_type.name} "{escaped_value}")'
