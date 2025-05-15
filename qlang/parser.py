"""
Recursive-descent parser for QLang
"""
import re
from ast import Program, Number, BinOp, Print

TOKEN_SPEC = [
    ('NUMBER',   r'\d+'),
    ('IDENT',    r'[A-Za-z_][A-Za-z0-9_]*'),
    ('PLUS',     r'\+'),
    ('MINUS',    r'-'),
    ('STAR',     r'\*'),
    ('SLASH',    r'/'),
    ('LPAREN',   r'\('),
    ('RPAREN',   r'\)'),
    ('SEMI',     r';'),
    ('SKIP',     r'[ \t\n]+'),
    ('MISMATCH', r'.'),
]
TOKEN_REGEX = '|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPEC)

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f'Token({self.type}, {self.value!r})'

class Parser:
    def __init__(self, text):
        self.tokens = list(self.tokenize(text))
        self.pos = 0

    def tokenize(self, text):
        for mo in re.finditer(TOKEN_REGEX, text):
            kind = mo.lastgroup
            value = mo.group()
            if kind == 'NUMBER':
                yield Token('NUMBER', int(value))
            elif kind == 'IDENT':
                yield Token('IDENT', value)
            elif kind == 'SKIP':
                continue
            elif kind == 'MISMATCH':
                raise SyntaxError(f'Unexpected character {value!r}')
            else:
                yield Token(kind, value)
        yield Token('EOF', '')

    def peek(self):
        return self.tokens[self.pos]

    def consume(self, *token_types):
        token = self.peek()
        if token.type in token_types:
            self.pos += 1
            return token
        else:
            expected = ' or '.join(token_types)
            raise SyntaxError(f'Expected {expected}, got {token.type}')

    def parse(self):
        statements = []
        while self.peek().type != 'EOF':
            statements.append(self.parse_statement())
        return Program(statements)

    def parse_statement(self):
        token = self.peek()
        if token.type == 'IDENT' and token.value == 'print':
            self.consume('IDENT')
            self.consume('LPAREN')
            expr = self.parse_expression()
            self.consume('RPAREN')
            self.consume('SEMI')
            return Print(expr)
        else:
            raise SyntaxError(f'Unknown statement at {token}')

    def parse_expression(self):
        node = self.parse_term()
        while self.peek().type in ('PLUS', 'MINUS'):
            op = self.consume('PLUS', 'MINUS').value
            right = self.parse_term()
            node = BinOp(node, op, right)
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.peek().type in ('STAR', 'SLASH'):
            op = self.consume('STAR', 'SLASH').value
            right = self.parse_factor()
            node = BinOp(node, op, right)
        return node

    def parse_factor(self):
        token = self.peek()
        if token.type == 'NUMBER':
            self.consume('NUMBER')
            return Number(token.value)
        elif token.type == 'LPAREN':
            self.consume('LPAREN')
            node = self.parse_expression()
            self.consume('RPAREN')
            return node
        else:
            raise SyntaxError(f'Unexpected token {token}')