from tokens import Token, TokenType
from tokenizer import Tokenizer


class Parser:
    def __init__(self, tokenizer: Tokenizer):
        self.tokenizer = tokenizer

    def parse_directive(self):
        pass
