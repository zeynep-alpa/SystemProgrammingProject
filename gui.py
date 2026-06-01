import tkinter as tk
from tkinter import filedialog
from lexer import Lexer
from parser import Parser

def format_ast(node, indent=0):
    space = "    " * indent

    if node is None:
        return space + "None\n"

    if isinstance(node, list):
        result = ""
        for item in node:
            result += format_ast(item, indent)
        return result

    node_type = node.get("type", "Unknown")

    if node_type == "Program":
        result = space + "Program\n"
        result += format_ast(node.get("body", []), indent + 1)
        return result

    if node_type == "Declaration":
        return space + f"Declaration: {node.get('var_type')} {node.get('name')}\n"

    if node_type == "Assignment":
        result = space + f"Assignment: {node.get('name')}\n"
        result += format_ast(node.get("value"), indent + 1)
        return result

    if node_type == "PrintStatement":
        result = space + "PrintStatement\n"
        result += format_ast(node.get("expression"), indent + 1)
        return result

    if node_type == "IfStatement":
        result = space + "IfStatement\n"
        result += space + "    Condition:\n"
        result += format_ast(node.get("condition"), indent + 2)
        result += space + "    If Body:\n"
        result += format_ast(node.get("if_body", []), indent + 2)
        result += space + "    Else Body:\n"
        result += format_ast(node.get("else_body", []), indent + 2)
        return result

    if node_type == "WhileStatement":
        result = space + "WhileStatement\n"
        result += space + "    Condition:\n"
        result += format_ast(node.get("condition"), indent + 2)
        result += space + "    Body:\n"
        result += format_ast(node.get("body", []), indent + 2)
        return result

    if node_type == "BinaryExpression":
        result = space + f"BinaryExpression: {node.get('operator')}\n"
        result += format_ast(node.get("left"), indent + 1)
        result += format_ast(node.get("right"), indent + 1)
        return result

    if node_type in ["IntegerLiteral", "FloatLiteral", "StringLiteral"]:
        return space + f"{node_type}: {node.get('value')}\n"

    if node_type == "Identifier":
        return space + f"Identifier: {node.get('name')}\n"

    return space + str(node) + "\n"


def analyze_code():
    code = code_text.get("1.0", tk.END)

    lexer = Lexer(code)
    tokens, symbol_table, lexical_errors = lexer.tokenize()

    parser = Parser(tokens, symbol_table)
    ast, parser_errors = parser.parse()

    token_text.delete("1.0", tk.END)
    symbol_text.delete("1.0", tk.END)
    error_text.delete("1.0", tk.END)
    ast_text.delete("1.0", tk.END)

    for token in tokens:
        token_text.insert(
            tk.END,
            f"{token.line:<4} | {token.value:<18} | {token.token_type}\n"
        )

    for name, info in symbol_table.items():
        symbol_text.insert(
            tk.END,
            f"{name:<12} | {info['type']:<8} | {info['scope']:<8} | {info['memory']}\n"
        )

    all_errors = lexical_errors + parser_errors

    if all_errors:
        for error in all_errors:
            error_text.insert(tk.END, error + "\n")
    else:
        error_text.insert(tk.END, "No errors found.\n")

    ast_text.insert(tk.END, format_ast(ast))


def open_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )

    if file_path:
        with open(file_path, "r", encoding="utf-8") as file:
            code_text.delete("1.0", tk.END)
            code_text.insert(tk.END, file.read())


def load_sample():
    sample_code = """int x;
int y;
float result;

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
    code_text.delete("1.0", tk.END)
    code_text.insert(tk.END, sample_code)


root = tk.Tk()
root.title("Simple Two-Pass Compiler")
root.geometry("1400x850")
root.minsize(1100, 800)

title_label = tk.Label(
    root,
    text="Simple Two-Pass Compiler",
    font=("Arial", 20, "bold")
)
title_label.pack(pady=8)

button_frame = tk.Frame(root)
button_frame.pack(pady=5)

tk.Button(button_frame, text="Open File", command=open_file, width=12).pack(side="left", padx=5)
tk.Button(button_frame, text="Load Sample", command=load_sample, width=12).pack(side="left", padx=5)
tk.Button(button_frame, text="Analyze", command=analyze_code, width=12).pack(side="left", padx=5)

main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True, padx=10, pady=5)

main_frame.rowconfigure(0, weight=1)
main_frame.rowconfigure(1, weight=0)
main_frame.columnconfigure(0, weight=1)

content_frame = tk.Frame(main_frame)
content_frame.grid(row=0, column=0, sticky="nsew")

error_area = tk.Frame(main_frame, height=90)
error_area.grid(row=1, column=0, sticky="ew", pady=5)
error_area.grid_propagate(False)

content_frame.rowconfigure(0, weight=60)
content_frame.rowconfigure(1, weight=40)
content_frame.columnconfigure(0, weight=1)
content_frame.columnconfigure(1, weight=1)

source_frame = tk.LabelFrame(content_frame, text="Source Code")
ast_frame = tk.LabelFrame(content_frame, text="AST / Parse Tree")
token_frame = tk.LabelFrame(content_frame, text="Token Stream")
symbol_frame = tk.LabelFrame(content_frame, text="Symbol Table")

source_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
ast_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
token_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
symbol_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

code_text = tk.Text(source_frame, font=("Consolas", 11), wrap="none")
code_text.pack(fill="both", expand=True, padx=5, pady=5)

ast_text = tk.Text(ast_frame, font=("Consolas", 10), wrap="none")
ast_text.pack(fill="both", expand=True, padx=5, pady=5)

token_text = tk.Text(token_frame, font=("Consolas", 9), wrap="none")
token_text.pack(fill="both", expand=True, padx=5, pady=5)

symbol_text = tk.Text(symbol_frame, font=("Consolas", 9), wrap="none")
symbol_text.pack(fill="both", expand=True, padx=5, pady=5)

error_frame = tk.LabelFrame(error_area, text="Errors")
error_frame.pack(fill="both", expand=True, padx=5)

error_text = tk.Text(error_frame, font=("Consolas", 10), wrap="none", height=4)
error_text.pack(fill="both", expand=True, padx=5, pady=5)

load_sample()

root.mainloop()