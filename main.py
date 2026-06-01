from lexer import Lexer
from parser import Parser
import json

code = """
int x;
int y;
float result;

// comment line
x = 10;
y = 3;
result = x + y * 2;

if (result > 15) {
    print("Result is large");
} else {
    print("Result is small");
}

while (x > 0) {
    x = x - 1;
}
"""

lexer = Lexer(code)
tokens, symbol_table, lexical_errors = lexer.tokenize()

parser = Parser(tokens, symbol_table)
ast, parser_errors = parser.parse()

print("TOKENS")
print("-" * 50)
for token in tokens:
    print(f"Line: {token.line:<3} Value: {token.value:<20} Type: {token.token_type}")

print("\nSYMBOL TABLE")
print("-" * 50)
for name, info in symbol_table.items():
    print(
        f"Name: {name:<10} "
        f"Type: {info['type']:<10} "
        f"Scope: {info['scope']:<10} "
        f"Memory: {info['memory']}"
    )

print("\nAST")
print("-" * 50)
print(json.dumps(ast, indent=4))

print("\nERRORS")
print("-" * 50)
all_errors = lexical_errors + parser_errors

if all_errors:
    for error in all_errors:
        print(error)
else:
    print("No errors found.")