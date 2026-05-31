from lexer import Lexer

code = """
int x;
int y;
float result;

// comment line
x = 10;
y = 3;
result = x + y * 2;

print("Result is large");
"""

lexer = Lexer(code)

tokens, symbol_table, errors = lexer.tokenize()

print("TOKENS")
print("-" * 40)

for token in tokens:
    print(
        f"Line: {token.line:<3} "
        f"Value: {token.value:<15} "
        f"Type: {token.token_type}"
    )

print("\nSYMBOL TABLE")
print("-" * 40)

for name, info in symbol_table.items():
    print(
        f"Name: {name:<10} "
        f"Type: {info['type']:<10} "
        f"Scope: {info['scope']:<10} "
        f"Memory: {info['memory']}"
    )

print("\nERRORS")
print("-" * 40)

if errors:
    for error in errors:
        print(error)
else:
    print("No lexical errors found.")