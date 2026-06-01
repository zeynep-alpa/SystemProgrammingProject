class Parser:
    def __init__(self, tokens, symbol_table):
        self.tokens = tokens
        self.symbol_table = symbol_table
        self.pos = 0
        self.errors = []

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def peek(self):
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return None

    def advance(self):
        if self.pos < len(self.tokens):
            self.pos += 1

    def is_at_end(self):
        token = self.current()
        return token is None or token.token_type == "EOF"

    def match_value(self, value):
        token = self.current()

        if token is not None and token.value == value:
            self.advance()
            return True

        return False

    def parse(self):
        program_node = {
            "type": "Program",
            "body": []
        }

        while not self.is_at_end():
            statement = self.parse_statement()

            if statement is not None:
                program_node["body"].append(statement)
            else:
                self.advance()

        return program_node, self.errors

    def parse_statement(self):
        token = self.current()

        if token is None:
            return None

        if token.value in ["int", "float"]:
            return self.parse_declaration()

        if token.token_type == "IDENTIFIER":
            return self.parse_assignment()

        if token.value == "print":
            return self.parse_print()

        if token.value == "if":
            return self.parse_if()

        if token.value == "while":
            return self.parse_while()

        self.errors.append(
            f"Line {token.line}: Unexpected token '{token.value}'"
        )
        self.advance()
        return None

    def parse_declaration(self):
        type_token = self.current()
        self.advance()

        identifier = self.current()

        if identifier is None or identifier.token_type != "IDENTIFIER":
            self.errors.append(
                f"Line {type_token.line}: Expected identifier after '{type_token.value}'"
            )
            return None

        variable_name = identifier.value
        self.advance()

        value_node = None
        value_type = None

        if self.match_value("="):
            value_node, value_type = self.parse_expression()

            if type_token.value == "int" and value_type == "float":
                self.errors.append(
                    f"Line {identifier.line}: Cannot assign float value to int variable '{variable_name}'"
                )

            if value_type == "string":
                self.errors.append(
                    f"Line {identifier.line}: Cannot assign string value to numeric variable '{variable_name}'"
                )

        if not self.match_value(";"):
            self.errors.append(
                f"Line {identifier.line}: Missing ';' after declaration"
            )
            self.synchronize()

        return {
            "type": "Declaration",
            "var_type": type_token.value,
            "name": variable_name,
            "value": value_node
        }

    def parse_assignment(self):
        identifier = self.current()
        variable_name = identifier.value

        if variable_name not in self.symbol_table:
            self.errors.append(
                f"Line {identifier.line}: Variable '{variable_name}' is not declared"
            )

        self.advance()

        if not self.match_value("="):
            self.errors.append(
                f"Line {identifier.line}: Expected '=' after identifier"
            )
            self.synchronize()
            return None

        expression_node, expression_type = self.parse_expression()

        if variable_name in self.symbol_table:
            variable_type = self.symbol_table[variable_name]["type"]

            if variable_type == "int" and expression_type == "float":
                self.errors.append(
                    f"Line {identifier.line}: Cannot assign float value to int variable '{variable_name}'"
                )

            if expression_type == "string":
                self.errors.append(
                    f"Line {identifier.line}: Cannot assign string value to numeric variable '{variable_name}'"
                )

        if not self.match_value(";"):
            self.errors.append(
                f"Line {identifier.line}: Missing ';' after assignment"
            )
            self.synchronize()

        return {
            "type": "Assignment",
            "name": variable_name,
            "value": expression_node
        }

    def parse_print(self):
        print_token = self.current()
        self.advance()

        if not self.match_value("("):
            self.errors.append(
                f"Line {print_token.line}: Expected '(' after print"
            )
            self.synchronize()
            return None

        expression_node, expression_type = self.parse_expression()

        if not self.match_value(")"):
            self.errors.append(
                f"Line {print_token.line}: Expected ')' after print expression"
            )
            self.synchronize()

        if not self.match_value(";"):
            self.errors.append(
                f"Line {print_token.line}: Missing ';' after print statement"
            )
            self.synchronize()

        return {
            "type": "PrintStatement",
            "expression": expression_node
        }

    def parse_if(self):
        if_token = self.current()
        self.advance()

        if not self.match_value("("):
            self.errors.append(
                f"Line {if_token.line}: Expected '(' after if"
            )
            self.synchronize()
            return None

        condition_node, condition_type = self.parse_expression()

        if not self.match_value(")"):
            self.errors.append(
                f"Line {if_token.line}: Expected ')' after if condition"
            )
            self.synchronize()

        if not self.match_value("{"):
            self.errors.append(
                f"Line {if_token.line}: Expected '{{' after if condition"
            )
            self.synchronize()
            return None

        if_body = []

        while not self.is_at_end() and self.current().value != "}":
            statement = self.parse_statement()

            if statement is not None:
                if_body.append(statement)
            else:
                self.advance()

        if not self.match_value("}"):
            self.errors.append(
                f"Line {if_token.line}: Expected '}}' after if block"
            )

        else_body = []

        if self.current() is not None and self.current().value == "else":
            self.advance()

            if not self.match_value("{"):
                self.errors.append(
                    f"Line {if_token.line}: Expected '{{' after else"
                )
                self.synchronize()
            else:
                while not self.is_at_end() and self.current().value != "}":
                    statement = self.parse_statement()

                    if statement is not None:
                        else_body.append(statement)
                    else:
                        self.advance()

                if not self.match_value("}"):
                    self.errors.append(
                        f"Line {if_token.line}: Expected '}}' after else block"
                    )

        return {
            "type": "IfStatement",
            "condition": condition_node,
            "if_body": if_body,
            "else_body": else_body
        }

    def parse_while(self):
        while_token = self.current()
        self.advance()

        if not self.match_value("("):
            self.errors.append(
                f"Line {while_token.line}: Expected '(' after while"
            )
            self.synchronize()
            return None

        condition_node, condition_type = self.parse_expression()

        if not self.match_value(")"):
            self.errors.append(
                f"Line {while_token.line}: Expected ')' after while condition"
            )
            self.synchronize()

        if not self.match_value("{"):
            self.errors.append(
                f"Line {while_token.line}: Expected '{{' after while condition"
            )
            self.synchronize()
            return None

        body = []

        while not self.is_at_end() and self.current().value != "}":
            statement = self.parse_statement()

            if statement is not None:
                body.append(statement)
            else:
                self.advance()

        if not self.match_value("}"):
            self.errors.append(
                f"Line {while_token.line}: Expected '}}' after while block"
            )

        return {
            "type": "WhileStatement",
            "condition": condition_node,
            "body": body
        }

    def parse_expression(self):
        return self.parse_logical_or()

    def parse_logical_or(self):
        left_node, left_type = self.parse_logical_and()

        while not self.is_at_end() and self.current().value == "||":
            operator = self.current()
            self.advance()

            right_node, right_type = self.parse_logical_and()

            left_node = {
                "type": "BinaryExpression",
                "operator": operator.value,
                "left": left_node,
                "right": right_node
            }
            left_type = "int"

        return left_node, left_type

    def parse_logical_and(self):
        left_node, left_type = self.parse_equality()

        while not self.is_at_end() and self.current().value == "&&":
            operator = self.current()
            self.advance()

            right_node, right_type = self.parse_equality()

            left_node = {
                "type": "BinaryExpression",
                "operator": operator.value,
                "left": left_node,
                "right": right_node
            }
            left_type = "int"

        return left_node, left_type

    def parse_equality(self):
        left_node, left_type = self.parse_comparison()

        while not self.is_at_end() and self.current().value in ["==", "!="]:
            operator = self.current()
            self.advance()

            right_node, right_type = self.parse_comparison()

            left_node = {
                "type": "BinaryExpression",
                "operator": operator.value,
                "left": left_node,
                "right": right_node
            }
            left_type = "int"

        return left_node, left_type

    def parse_comparison(self):
        left_node, left_type = self.parse_term()

        while not self.is_at_end() and self.current().value in ["<", ">", "<=", ">="]:
            operator = self.current()
            self.advance()

            right_node, right_type = self.parse_term()

            left_node = {
                "type": "BinaryExpression",
                "operator": operator.value,
                "left": left_node,
                "right": right_node
            }
            left_type = "int"

        return left_node, left_type

    def parse_term(self):
        left_node, left_type = self.parse_factor()

        while not self.is_at_end() and self.current().value in ["+", "-"]:
            operator = self.current()
            self.advance()

            right_node, right_type = self.parse_factor()

            left_node = {
                "type": "BinaryExpression",
                "operator": operator.value,
                "left": left_node,
                "right": right_node
            }

            if left_type == "float" or right_type == "float":
                left_type = "float"
            else:
                left_type = "int"

        return left_node, left_type

    def parse_factor(self):
        left_node, left_type = self.parse_primary()

        while not self.is_at_end() and self.current().value in ["*", "/"]:
            operator = self.current()
            self.advance()

            right_node, right_type = self.parse_primary()

            left_node = {
                "type": "BinaryExpression",
                "operator": operator.value,
                "left": left_node,
                "right": right_node
            }

            if left_type == "float" or right_type == "float" or operator.value == "/":
                left_type = "float"
            else:
                left_type = "int"

        return left_node, left_type

    def parse_primary(self):
        token = self.current()

        if token is None:
            self.errors.append("Unexpected end of input")
            return None, "unknown"

        if token.token_type == "INTEGER_LITERAL":
            self.advance()
            return {
                "type": "IntegerLiteral",
                "value": token.value
            }, "int"

        if token.token_type == "FLOAT_LITERAL":
            self.advance()
            return {
                "type": "FloatLiteral",
                "value": token.value
            }, "float"

        if token.token_type == "STRING_LITERAL":
            self.advance()
            return {
                "type": "StringLiteral",
                "value": token.value
            }, "string"

        if token.token_type == "IDENTIFIER":
            variable_name = token.value

            if variable_name not in self.symbol_table:
                self.errors.append(
                    f"Line {token.line}: Variable '{variable_name}' is not declared"
                )
                variable_type = "unknown"
            else:
                variable_type = self.symbol_table[variable_name]["type"]

            self.advance()

            return {
                "type": "Identifier",
                "name": variable_name
            }, variable_type

        if token.value == "(":
            self.advance()
            expression_node, expression_type = self.parse_expression()

            if not self.match_value(")"):
                self.errors.append(
                    f"Line {token.line}: Expected ')' after expression"
                )

            return expression_node, expression_type

        self.errors.append(
            f"Line {token.line}: Unexpected token in expression '{token.value}'"
        )
        self.advance()

        return None, "unknown"

    def synchronize(self):
        while True:
            token = self.current()

            if token is None:
                return

            if token.token_type == "EOF":
                return

            if token.value == ";":
                self.advance()
                return

            if token.value == "}":
                return

            self.advance()