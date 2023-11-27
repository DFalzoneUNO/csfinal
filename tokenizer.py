from typing import List
from tokens import TokenType, Token


class TokenError(Exception):
    """Exception class for errors encountered while tokenizing Narrate source code."""
    def __init__(self, line_number: int, message: str):
        super().__init__(
            f"TokenError on line {line_number}: {message}"
        )


class Tokenizer:
    def __init__(self, text: str):
        """The argument to the constructor for the Tokenizer class is the full text
        of the file to be tokenized.
        """
        self.text: str = text
        self.current_position: int = 0
        self.current_line: int = 1

    @property
    def current_char(self) -> str | None:
        """This property returns the character at the currently selected position
        in the text, or None if the end of the text has been reached.
        """
        if self.current_position >= len(self.text):
            return None
        else:
            return self.text[self.current_position]

    @property
    def next_char(self) -> None | str:
        """This property returns the character directly following the currently
        selected position in the text, or `None` if that position would be past
        the end of the text.
        """
        if self.current_position + 1 >= len(self.text):
            return None
        else:
            return self.text[self.current_position + 1]

    def advance(self):
        """Advance the currently selected character position one unit forward and
        update the current line number if a newline is reached.
        """
        if self.current_char == '\n':
            self.current_line += 1
        self.current_position += 1

    def skip_whitespace(self):
        """If the current char is a whitespace character, move forward until it isn't."""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        """If the current char is the comment sigil '#', move to the next uncommented line."""
        while self.current_char == '#':
            while self.current_char != '\n':
                self.advance()
            self.advance()

    @staticmethod
    def truncate_spaces(string: str) -> str:
        """Replace any sequence of N spaces in a string with 1 space
        for any value of N."""
        result = string
        while "  " in result:
            result = result.replace("  ", " ")
        return result

    def tokenize_string(self) -> Token:
        """Tokenize a string literal enclosed in double quotes. This method should only
        be called if the current char is a double quotation mark. String literals may include
        the escape sequences for a newline, a tab character, or a double quotation mark.
        """
        string_characters = ""
        self.advance()
        while self.current_char != '"':
            if self.current_char == '\\':
                self.advance()
                if self.current_char == 'n':
                    string_characters += '\n'
                    self.current_line += 1
                elif self.current_char == 't':
                    string_characters += '\t'
                elif self.current_char == '"':
                    string_characters += '"'
                else:
                    raise TokenError(
                        self.current_line,
                        f"Unrecognized escape sequence \\{self.current_char}"
                    )
            else:
                string_characters += str(self.current_char)
            self.advance()
        self.advance()
        return Token(
            TokenType.String,
            Tokenizer.truncate_spaces(string_characters)
        )

    def tokenize_delimeter(self) -> Token:
        """Tokenize a "delimeter", which is any of the Narrate keywords that begin
        with the sigil '@'. These keywords define the structure of a Narrate program
        in terms of modules, scenes, and files."""
        delimeter: str = str(self.current_char)
        self.advance()
        while self.current_char is not None and (
            self.current_char.isalpha() or self.current_char == '-'
        ):
            delimeter += self.current_char
            self.advance()
        valid_delimeters = ("@module", "@end-module", "@scene", "@end-scene", "@file")
        if delimeter in valid_delimeters:
            return Token(TokenType(delimeter))
        else:
            raise TokenError(
                self.current_line,
                f"Expected valid delimeter, got '{delimeter}' instead."
            )

    def tokenize_identifier_or_directive(self) -> Token:
        """If the current char happens to be the start of one of Narrate's "directives",
        it returns a directive token. Otherwise it will return an identifier token or raise
        a TokenError.
        
        In contrast to delimeters which organize the code and define its structure, directives
        define the behavior of a scene: its flavortext, the options it presents to the player,
        manipulations to the player's inventory, and conditional logic. Directive keywords
        don't start with a sigil.

        Identifiers are used to identify scenes and modules. They must start with an
        alphanumeric character and contain only alphanumeric characters or dashes. Directive
        keywords are reserved and cannot be used as identifiers.
        """
        token_value = ""
        while self.current_char is not None and (
            self.current_char.isalpha() or self.current_char == '-'
        ):
            token_value += self.current_char
            self.advance()
        if token_value in ("flavortext", "select", "get", "lose", "has", "no"):
            return Token(TokenType(token_value))
        elif all(char.isalnum() or char == '-' for char in token_value):
            return Token(TokenType.Identifier, token_value)
        else:
            raise TokenError(
                self.current_line,
                f"Expected directive or identifier, got {token_value}"
            )

    def tokenize_punctuation(self) -> Token:
        """Assuming the current char is a punctuation character, identify which punctuation
        mark it is, and return the corresponding token, leaving the currently selected position
        directly after it.
        """
        if self.current_char == ':':
            self.advance()
            if self.current_char == ':':
                self.advance()
                return Token(TokenType.Scope)
            else:
                return Token(TokenType.Colon)
        elif self.current_char == '=':
            self.advance()
            if self.current_char == '>':
                self.advance()
                return Token(TokenType.Arrow)
            else:
                raise TokenError(self.current_line, f"Unexpected sequence '={self.current_char}'")
        elif self.current_char in (';', ',', '?', '{', '}', '(', ')'):
            char = self.current_char
            self.advance()
            return Token(TokenType(char))
        else:
            raise TokenError(self.current_line, f"Unexpected character '{self.current_char}'")

    def get_next_token(self) -> Token:
        """Get the next token from the tokenizer, leaving the currently selected position
        at the beginning of the next token, or at the end of the file if there are no more
        tokens.
        """
        if self.current_char is None:
            return Token(TokenType.Eof)
        elif self.current_char.isspace():
            self.skip_whitespace()
            return self.get_next_token()
        elif self.current_char == '#':
            self.skip_comment()
            return self.get_next_token()
        elif self.current_char == '@':
            return self.tokenize_delimeter()
        elif self.current_char == '"':
            return self.tokenize_string()
        elif self.current_char.isalnum():
            return self.tokenize_identifier_or_directive()
        else:
            return self.tokenize_punctuation()

    def tokenize(self, debug_mode: bool = False) -> List[Token]:
        """Return the entirety of the text as a list of tokens.
        If `debug_mode=True`, print each token as it is gotten.
        """
        result: List[Token] = []
        while len(result) == 0 or result[-1].token_type is not TokenType.Eof:
            token = self.get_next_token()
            if debug_mode:
                print(token)
            result.append(token)
        return result
