import re
from enum import Enum, auto


# https://stackoverflow.com/a/51226342/10942736
class TokenType(Enum):
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

    QuoteString = auto(),
    LongText = auto(),
    Identifier = auto()


class Token:
    Keywords = [
        TokenType.Module, TokenType.EndModule,
        TokenType.Scene, TokenType.EndScene,
        TokenType.FileReference,
        TokenType.Flavortext,
        TokenType.Select,
        TokenType.Has,
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
        self.token_type = token_type
        if token_type in (TokenType.QuoteString, TokenType.LongText, TokenType.Identifier):
            if value is None:
                raise ValueError("Token type expects string value but none was given")
            else:
                self.value = value
        else:
            self.value = token_type.value[0]

    def __str__(self):
        if self.token_type in Token.Keywords:
            return f"(Keyword {self.value})"
        elif self.token_type in Token.Punctuation:
            return f"(Punctuation {self.value})"
        else:
            return f'({self.token_type.name} "{re.escape(self.value)}")'
