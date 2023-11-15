from tokens import TokenType, Token


# The lexer takes Narrate source code and returns a stream of tokens.
class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.index = 0
        self.current_char = self.text[self.index]


