KEYWORDS = {"int", "float", "if", "else", "while", "print"}

OPERATORS = {
    "=", "+", "-", "*", "/",
    "==", "!=", "<", ">", "<=", ">=",
    "&&", "||"
}

DELIMITERS = {";", "(", ")", "{", "}", ","}


class Token:
    def __init__(self, line, value, token_type):
        self.line = line
        self.value = value
        self.token_type = token_type

    def __repr__(self):
        return f"[{self.token_type} '{self.value}' line:{self.line}]"


class Lexer:
    def __init__(self, source):
        self.source = source
        self.pos = 0
        self.line = 1
        self.tokens = []
        self.errors = []

        self.symbol_table = {}
        self.memory_address = 1000

    def current(self):
        if self.pos < len(self.source):
            return self.source[self.pos]
        return None

    def peek(self):
        next_pos = self.pos + 1

        if next_pos < len(self.source):
            return self.source[next_pos]

        return None

    def advance(self):
        ch = self.source[self.pos]
        self.pos += 1

        if ch == "\n":
            self.line += 1

        return ch

    def skip_whitespace(self):
        while self.current() is not None and self.current() in " \t\r\n":
            self.advance()

    def read_number(self):
        number = ""
        dot_count = 0
        start_line = self.line

        while self.current() is not None and (
            self.current().isdigit() or self.current() == "."
        ):
            if self.current() == ".":
                dot_count += 1

            number += self.advance()

        if dot_count > 1:
            self.errors.append(
                f"Line {start_line}: Malformed number '{number}'"
            )
            return Token(start_line, number, "INVALID_NUMBER")

        if number.startswith(".") or number.endswith("."):
            self.errors.append(
                f"Line {start_line}: Malformed number '{number}'"
            )
            return Token(start_line, number, "INVALID_NUMBER")

        if dot_count == 1:
            return Token(start_line, number, "FLOAT_LITERAL")

        return Token(start_line, number, "INTEGER_LITERAL")

    def read_string(self):
        start_line = self.line
        self.advance()
        text = ""

        while self.current() is not None and self.current() != '"':
            if self.current() == "\n":
                self.errors.append(
                    f"Line {start_line}: Unterminated string literal"
                )
                return Token(start_line, text, "INVALID_STRING")

            text += self.advance()

        if self.current() == '"':
            self.advance()
            return Token(start_line, text, "STRING_LITERAL")

        self.errors.append(
            f"Line {start_line}: Unterminated string literal"
        )
        return Token(start_line, text, "INVALID_STRING")

    def read_identifier_or_keyword(self):
        word = ""
        start_line = self.line

        while self.current() is not None and (
            self.current().isalnum() or self.current() == "_"
        ):
            word += self.advance()

        if word in KEYWORDS:
            return Token(start_line, word, "KEYWORD")

        return Token(start_line, word, "IDENTIFIER")

    def tokenize(self):
        while self.pos < len(self.source):
            self.skip_whitespace()

            if self.pos >= len(self.source):
                break

            ch = self.current()

            if ch.isdigit():
                self.tokens.append(self.read_number())

            elif ch.isalpha() or ch == "_":
                self.tokens.append(self.read_identifier_or_keyword())

            elif ch == '"':
                self.tokens.append(self.read_string())

            elif ch == "/" and self.peek() == "/":
                while self.current() is not None and self.current() != "\n":
                    self.advance()

            elif ch == "=" and self.peek() == "=":
                self.advance()
                self.advance()
                self.tokens.append(Token(self.line, "==", "OPERATOR"))

            elif ch == "!" and self.peek() == "=":
                self.advance()
                self.advance()
                self.tokens.append(Token(self.line, "!=", "OPERATOR"))

            elif ch == "<" and self.peek() == "=":
                self.advance()
                self.advance()
                self.tokens.append(Token(self.line, "<=", "OPERATOR"))

            elif ch == ">" and self.peek() == "=":
                self.advance()
                self.advance()
                self.tokens.append(Token(self.line, ">=", "OPERATOR"))

            elif ch == "&" and self.peek() == "&":
                self.advance()
                self.advance()
                self.tokens.append(Token(self.line, "&&", "OPERATOR"))

            elif ch == "|" and self.peek() == "|":
                self.advance()
                self.advance()
                self.tokens.append(Token(self.line, "||", "OPERATOR"))

            elif ch in OPERATORS:
                self.advance()
                self.tokens.append(Token(self.line, ch, "OPERATOR"))

            elif ch in DELIMITERS:
                self.advance()
                self.tokens.append(Token(self.line, ch, "DELIMITER"))

            else:
                self.errors.append(
                    f"Line {self.line}: Invalid character '{ch}'"
                )
                self.advance()

        self.tokens.append(Token(self.line, "EOF", "EOF"))

        self.build_symbol_table()

        return self.tokens, self.symbol_table, self.errors

    def build_symbol_table(self):
        for i in range(len(self.tokens) - 2):
            current_token = self.tokens[i]
            next_token = self.tokens[i + 1]
            third_token = self.tokens[i + 2]

            if (
                current_token.value in {"int", "float"}
                and current_token.token_type == "KEYWORD"
                and next_token.token_type == "IDENTIFIER"
            ):
                variable_name = next_token.value
                variable_type = current_token.value

                if variable_name in self.symbol_table:
                    self.errors.append(
                        f"Line {next_token.line}: Duplicate variable declaration '{variable_name}'"
                    )
                else:
                    self.symbol_table[variable_name] = {
                        "type": variable_type,
                        "scope": "global",
                        "memory": self.memory_address
                    }

                    self.memory_address += 4
